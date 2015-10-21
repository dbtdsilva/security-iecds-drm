/**
 * Created by pmec on 04/02/15.
 */
/**=========================================================
 * Module: websocket.js
 * Wraps the built-in WebSocket
 =========================================================*/

function noop() {}

// Wraps the built-in WebSocket into a replaceable provider suitable for dependency injection.
App.service('$websocket', function() {
	var ws;
	this.connect = function(url) {
		ws = new WebSocket(url);
		ws.onopen = this.onopen;
		ws.onmessage = this.onmessage;
		ws.onerror = this.onerror;
		ws.onclose = this.onclose;
	};
	this.send = function(msg) {
		ws.send(msg);
	};
	this.close = function() {
		ws.close();
	};
});

function FactoryWebSocket($q, $timeout, $interval, _console, websocket_uri, heartbeat_msg) {
  var ws;
  var ws_url, deferred, scope, collection, facility;
  var is_subscriber = false, is_publisher = false, receiving = false;
  var wait_for_reconnect = 0, heartbeat_promise = null, missed_heartbeats = 0;

  function _connect() {
    _console.log("Connecting to "+ws_url);
    deferred = $q.defer();
    ws = new WebSocket(ws_url);
    ws.onopen = onopen;
		ws.onmessage = onmessage;
		ws.onerror = onerror;
		ws.onclose = onclose;
  }

  function onopen(evt) {
    _console.log('Connected ' + facility);
    deferred.resolve();
    wait_for_reconnect = 0;
    if (heartbeat_msg && heartbeat_promise === null) {
      missed_heartbeats = 0;
      heartbeat_promise = $interval(_sendHeartbeat, 5000);
    }
  }

  function onclose(evt) {
    _console.log("Disconnected " + facility);
    deferred.reject();
    wait_for_reconnect = Math.min(wait_for_reconnect + 1000, 10000);
    $timeout(function() {
      _connect();
    }, wait_for_reconnect);
  }

  function onerror(evt) {
    _console.error("Websocket connection is broken! " + facility);
    ws.close();
  }

  function onmessage(evt) {
    //_console.log("Received " + facility, evt.data);
    var data;
    if (evt.data === heartbeat_msg) {
      // reset the counter for missed heartbeats
      missed_heartbeats = 0;
      return;
    }
    try {
      data = angular.fromJson(evt.data);
    } catch(e) {
      _console.warn('Data received by server is invalid '  + facility + ' JSON: ' + evt.data);
      return;
    }
    if (is_subscriber) {
      // temporarily disable the function 'listener', so that message received
      // from the websocket, are not propagated back
      receiving = true;
      scope.$apply(function() {
        angular.extend(scope[collection], data);
      });
      receiving = false;
    }
  }

  function _sendHeartbeat() {
    try {
      missed_heartbeats++;
      if (missed_heartbeats > 3)
        throw new Error("Too many missed heartbeats. " + facility);
      ws.send(heartbeat_msg);
    } catch(e) {
      $interval.cancel(heartbeat_promise);
      heartbeat_promise = null;
      _console.warn("Closing connection. " + facility + " Reason: " + e.message);
      ws.close();
    }
  }

  function _listener(newValue, oldValue) {
    if (!receiving && !angular.equals(oldValue, newValue)) {
      ws.send(angular.toJson(newValue));
    }
  }

  function _setChannels(channels) {
    angular.forEach(channels, function(channel) {
      if (channel.substring(0, 9) === 'subscribe') {
        is_subscriber = true;
      } else if (channel.substring(0, 7) === 'publish') {
        is_publisher = true;
      }
    });
  }

  function _watchCollection() {
    scope.$watchCollection(collection, _listener);
  }

  function _buildWebSocketURL(facility, channels) {
    var parts = [websocket_uri, facility, '?'];
    parts.push(channels.join('&'));
    ws_url = parts.join('');
  }

  this.connect = function($scope, scope_obj, facility_id, channels) {
    scope = $scope;
    _setChannels(channels);
    collection = scope_obj;
    scope[collection] = scope[collection] || {};
    facility = facility_id;
    _buildWebSocketURL(facility, channels);
    _connect();
    if (is_publisher) {
      deferred.promise.then(_watchCollection);
    }
    return deferred.promise;
  };
}

App.factory('WebSocketHelper', ['$q', '$timeout', '$interval', function($q, $timeout, $interval) {
  return function(websocket_uri, heartbeat_msg, logLevel) {
    var _console = { log: noop, warn: noop, error: noop };
    switch (logLevel) {
		case 'debug':
			_console = console;
			break;
		case 'log':
			_console.log = console.log;
			/* falls through */
		case 'warn':
			_console.warn = console.warn;
			/* falls through */
		case 'error':
			_console.error = console.error;
			/* falls through */
		default:
			break;
		}
    return new FactoryWebSocket($q, $timeout, $interval, _console, websocket_uri, heartbeat_msg)
  };
}]);