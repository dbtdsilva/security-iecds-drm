/**=========================================================
 * Module: main.js
 * Main Application Controller
 =========================================================*/
App.controller('AppController',
    ['$rootScope', '$scope', '$state', '$translate', '$window', '$localStorage', '$timeout', '$location', '$http', 'toggleStateService', 'colors', 'browser', 'cfpLoadingBar', 'AuthService', 'toaster',
        function ($rootScope, $scope, $state, $translate, $window, $localStorage, $timeout, $location, $http, toggle, colors, browser, cfpLoadingBar, AuthService, toaster) {
            "use strict";


            $rootScope.$watch('AuthService.isLogged', function () {
                if (!AuthService.isLogged)
                    return;

                /**************************************************
                 ***************** NOTIFICATIONS ******************
                 **************************************************/
                $rootScope.last_notifications = {
                    list: [],
                    extendedList: [],
                    unread: 0,
                    total: 0,
                    settings: {
                        page_size: 10,
                        page: 1,
                        pages_total: 0
                    }
                };

                $rootScope.markMessageAs = function (notification_id, read, readAll) {
                    $http.patch('api/dashboard/notification/user/', {
                        id: notification_id,
                        read: read,
                        readAll: readAll
                    }).then(function (response, status, headers, config) {
                        $rootScope.updateAllNotifications();
                    }, function (response, status, headers, config) {
                        console.log("Failed to load notifications");
                    });
                }

                $rootScope.markAllAsRead = function() {
                    for (var notification in $rootScope.last_notifications.extendedList) {
                        if (!notification.read) {
                             $http.patch('api/dashboard/notification/user/', {
                                id: notification.id,
                                read: true,
                                readAll: true
                            }).then(function (response, status, headers, config) {
                                $rootScope.updateAllNotifications();
                            }, function (response, status, headers, config) {
                                console.log("Failed to load notifications");
                            });
                        }

                    }
                }
                $rootScope.$watch('last_notifications.settings.page', function () {
                    $rootScope.loadNotificationPage();
                    $("body").animate({scrollTop: 70}, "slow");
                });
                $rootScope.loadNotificationPage = function () {
                    $http.get('api/dashboard/notification/user/?page=' + $rootScope.last_notifications.settings.page +
                        '&page_size=' + $rootScope.last_notifications.settings.page_size, {}).then(
                        function (response, status, headers, config) {
                            $rootScope.last_notifications.extendedList = [];
                            $rootScope.last_notifications.total = response.data.count;
                            $rootScope.last_notifications.settings.pages_total =
                                Math.ceil(response.data.count / $rootScope.last_notifications.settings.page_size);
                            angular.forEach(response.data.results, function (val) {
                                val.notification.title = JSON.parse(val.notification.title);
                                val.notification.message = JSON.parse(val.notification.message);
                                val.notification.timestamp = new Date(val.notification.timestamp).toLocaleString();
                                $rootScope.last_notifications.extendedList.push(val);
                            });
                            console.log($rootScope.last_notifications);
                        }, function (response, status, headers, config) {
                            console.log("Failed to load notifications");
                        });
                }
                $rootScope.loadNotifications = function () {
                    $http.get('api/dashboard/notification/user/?page_size=5', {}).then(function (response, status, headers, config) {
                        $rootScope.last_notifications.list = [];
                        $rootScope.last_notifications.total = response.data.count;
                        $rootScope.last_notifications.settings.pages_total =
                            Math.ceil(response.data.count / $rootScope.last_notifications.settings.page_size);
                        angular.forEach(response.data.results, function (val) {
                            val.notification.title = JSON.parse(val.notification.title);
                            val.notification.message = JSON.parse(val.notification.message);
                            val.notification.timestamp = new Date(val.notification.timestamp).toLocaleString();
                            $rootScope.last_notifications.list.push(val);
                        });
                        console.log($rootScope.last_notifications);
                    }, function (response, status, headers, config) {
                        console.log("Failed to load notifications");
                    });
                }

                $rootScope.getUnreadMessages = function () {
                    $http.get('api/dashboard/notification/user/?read=False&page_size=1', {}).then(
                        function (response, status, headers, config) {
                            $rootScope.last_notifications.unread = response.data.count;
                        }, function (response, status, headers, config) {
                            console.log("Failed to load notifications");
                        });
                }

                $rootScope.updateAllNotifications = function () {
                    $rootScope.loadNotifications();
                    $rootScope.getUnreadMessages();
                    $rootScope.loadNotificationPage();
                }
                $rootScope.updateAllNotifications();
                /**************************************************
                 *********************** MQTT *********************
                 **************************************************/
                var host = 'io.atnog.org';
                var port = 443;
                var useTLS = true;
                if ($location.protocol() === 'http') {
                    useTLS = false;
                    port = 80;
                }
                $rootScope.base_url = '';
                var hostHttp = $location.host();
                if (hostHttp === 'localhost' || hostHttp === '127.0.0.1' || hostHttp === '193.136.93.43') {
                    $rootScope.base_url = 'api/proxy/io.atnog.org/';
                }
                $rootScope.base_topic = 'CqV5fzAUyyXP7gNjmq72pq/r13DCS8FfSwM0jeXeDgQZV/EBEK9ks7M388Mi9BxN4Cmx/';  // topic to subscribe to
                var topic = $rootScope.base_topic + '#';  // topic to subscribe to
                $rootScope.apiKey = 'WzdusBbyhYMNw7AUGsZ0hSLWlC14kPy2';
                var username = $rootScope.apiKey;
                var password = $rootScope.apiKey;
                var cleanSession = true;
                var mqtt;
                var reconnectTimeout = 2000;
                $scope.libeliumSensorNames = {};
                $scope.lastKnownMessages = {};

                $http.get("server/sensor-names.json", {}).then(function (response, status, headers, config) {
                    var list = {};
                    list = response.data;
                    console.log("D:");
                    $http.get("server/custom-sensor-names.json", {}).then(function (response, status, headers, config) {
                        $scope.libeliumSensorNames = angular.extend(list, response.data);
                        console.log($scope.libeliumSensorNames);
                    }, function (response, status, headers, config) {
                        console.error(response);
                    });
                }, function (response, status, headers, config) {
                    console.error(response);
                });

                function registerLastKnownMessage(device, topic, timestamp, payload) {
                    if (!angular.isDefined(device) || !angular.isDefined(topic) || !angular.isDefined(timestamp) || !angular.isDefined(payload) ||
                        timestamp <= 0)
                        return;
                    if (!angular.isDefined($scope.lastKnownMessages[device]))
                        $scope.lastKnownMessages[device] = {};
                    if (!angular.isDefined($scope.lastKnownMessages[device][topic])) {
                        $scope.lastKnownMessages[device][topic] = {
                            timestamp: 0,
                            payload: {}
                        };
                    }
                    if (timestamp > $scope.lastKnownMessages[device][topic].timestamp) {
                        $scope.lastKnownMessages[device][topic].timestamp = timestamp;
                        $scope.lastKnownMessages[device][topic].payload = payload;
                    }

                }

                $http.get('api/dashboard/devices/all/', {}).then(function (response, status, headers, config) {
                    var data = response.data;
                    angular.forEach(data, function (device) {
                        var key = '&api_key=' + $rootScope.apiKey;
                        var url = $rootScope.base_url + 'data/' + $rootScope.base_topic +
                            device.uuid + '?b=5m&q=["payload","topic"]&m=1&k=1' + key;
                        $http.get(url, {}).then(function (response, status, headers, config) {
                            angular.forEach(response.data.results, function (element) {
                                var tmp = element.topic.replace($rootScope.base_topic, '').split("/");
                                var topic = tmp[1];
                                if (!angular.isDefined(element.payload) || !angular.isDefined(element.payload.timestamp))
                                    return;
                                registerLastKnownMessage(device.uuid, topic,
                                    element.payload.timestamp, element.payload);
                            });
                        });
                    });
                }, function (response, status, headers, config) {
                    console.error(response);
                });

                $scope.MQTTConnect = function () {
                    mqtt = new Paho.MQTT.Client(host, port, "/mqtt", 'web_' + parseInt(Math.random() * 100, 10));
                    var options = {
                        timeout: 3,
                        useSSL: useTLS,
                        cleanSession: cleanSession,
                        onSuccess: onConnect,
                        onFailure: function (message) {
                            console.error('MQTT Connection failed: ' + message.errorMessage + 'Retrying');
                            setTimeout($scope.MQTTConnect, reconnectTimeout);
                        }
                    };

                    mqtt.onConnectionLost = onConnectionLost;
                    mqtt.onMessageArrived = onMessageArrived;

                    if (username != null) {
                        options.userName = username;
                        options.password = password;
                    }
                    console.log('MQTT Connecting host:', host, 'port', port, 'TLS', useTLS);
                    mqtt.connect(options);
                }

                function onConnect() {
                    console.log('MQTT Connected to ', host, ':', port);
                    // Connection succeeded; subscribe to our topic
                    mqtt.subscribe(topic, {qos: 0});
                    console.log('MQTT Subscribing to topic', topic);
                }

                function onConnectionLost(response) {
                    setTimeout($scope.MQTTConnect, reconnectTimeout);
                    console.error('MQTT Connection lost: ', response.errorMessage, '. Reconnecting');
                }

                function onMessageArrived(message) {
                    var stream = message.destinationName.replace($rootScope.base_topic, '');
                    var payload = angular.fromJson(message.payloadString);
                    $scope.$apply(function () {
                        $scope.processMessage(stream, payload);
                    });
                    //console.log($scope.lastKnownMessages);

                }

                $scope.processMessage = function (stream, payload) {
                    var val = stream.split("/");
                    var topic = val[1];
                    var device = val[0];

                    if (!angular.isDefined(payload) || !angular.isDefined(payload.timestamp))
                        return;
                    if (topic == "notification") {
                        console.log("Notification received!", payload);
                        toaster.pop((angular.isDefined(payload.type) ? payload.type : "info"),
                            payload.title[$scope.language.selected.localeId],
                            payload.message[$scope.language.selected.localeId]);
                        $rootScope.last_notifications.unread++;
                        $timeout(function () {
                            $rootScope.updateAllNotifications();
                        }, 5000);
                    } else {
                        registerLastKnownMessage(device, topic, payload.timestamp, payload);
                    }
                }
                $scope.MQTTConnect();
            }, true);


            /**************************************************
             ***************** APPLICATION ********************
             **************************************************/
                // Setup the layout mode
            $rootScope.app.layout.horizontal = ( $rootScope.$stateParams.layout == 'app-h');

            $rootScope.cfpLoadingBar = cfpLoadingBar;
            // Loading bar transition
            // -----------------------------------
            var thBar;
            $rootScope.$on('$stateChangeStart', function (event, toState, toParams, fromState, fromParams) {
                if ($('.wrapper > section').length) // check if bar container exists
                    thBar = $timeout(function () {
                        cfpLoadingBar.start();
                    }, 0); // sets a latency Threshold

                /**
                 * $stateChangeStart is a synchronous check to the accessLevels property
                 * if it's not set, it will setup a pendingStateChange and will let
                 * the grandfather resolve do his job.
                 *
                 * In short:
                 * If accessLevels is still undefined, it let the user change the state.
                 * Grandfather.resolve will either let the user in or reject the promise later!
                 */
                if (AuthService.userRole === null) {
                    AuthService.doneLoading = false;
                    AuthService.pendingStateChange = {
                        toState: toState,
                        toParams: toParams
                    };
                    return;
                }

                // if the state has undefined accessLevel, anyone can access it.
                // NOTE: if `wrappedService.userRole === undefined` means the service still doesn't know the user role,
                // we need to rely on grandfather resolve, so we let the stateChange success, for now.
                if (AuthService.canAccess(toState.accessLevel)) {
                    angular.noop(); // requested state can be transitioned to.
                } else {
                    event.preventDefault();
                    $rootScope.$emit('$statePermissionError');
                    $timeout.cancel(thBar);
                    cfpLoadingBar.complete();
                    //$state.go(AuthService.errorState, { error: 'unauthorized' }, { location: false, inherit: false });
                    $state.go(AuthService.errorState, {error: 'unauthorized'});
                }

            });
            $rootScope.$on('$stateChangeSuccess', function (event, toState, toParams, fromState, fromParams) {
                event.targetScope.$watch("$viewContentLoaded", function () {
                    $timeout.cancel(thBar);
                    cfpLoadingBar.complete();
                });
            });


            // Hook not found
            $rootScope.$on('$stateNotFound', function (event, unfoundState, fromState, fromParams) {
                console.log('$stateNotFound');
                console.log(unfoundState.to); // "lazy.state"
                console.log(unfoundState.toParams); // {a:1, b:2}
                console.log(unfoundState.options); // {inherit:false} + default options
            });
            // Hook error
            $rootScope.stateChangeErrorCout = 0;
            /**
             * Gets triggered when a resolve isn't fulfilled
             * NOTE: when the user doesn't have required permissions for a state, this event
             *       it's not triggered.
             *
             * In order to redirect to the desired state, the $http status code gets parsed.
             * If it's an HTTP code (ex: 403), could be prefixed with a string (ex: resolvename403),
             * to handle same status codes for different resolve(s).
             * This is defined inside $state.redirectMap.
             */
            $rootScope.$on('$stateChangeError', function (event, toState, toParams, fromState, fromParams, error) {
                console.log('$stateChangeError', error);
                $rootScope.stateChangeErrorCout++;
                if ($rootScope.stateChangeErrorCout > 4) return;
                //return $state.go(AuthService.errorState, { error: error }, { location: false, inherit: false });
                /**
                 * This is a very clever way to implement failure redirection.
                 * You can use the value of redirectMap, based on the value of the rejection
                 * So you can setup DIFFERENT redirections based on different promise errors.
                 */
                var redirectObj;
                // in case the promise given to resolve function is an $http request
                // the error is a object containing the error and additional informations
                error = (typeof error === 'object') ? error.status + '' : error;
                // in case of a random 4xx/5xx status code from server, user gets loggedout
                // otherwise it *might* forever loop (look call diagram)
                if (/^[45]\d{2}$/.test(error)) {
                    AuthService.logout();
                }
                /**
                 * Generic redirect handling.
                 * If a state transition has been prevented and it's not one of the 2 above errors, means it's a
                 * custom error in your application.
                 *
                 * redirectMap should be defined in the $state(s) that can generate transition errors.
                 */
                if (angular.isDefined(toState.redirectMap) && angular.isDefined(toState.redirectMap[error])) {
                    if (typeof toState.redirectMap[error] === 'string') {
                        return $state.go(toState.redirectMap[error], {error: error}, {location: false, inherit: false});
                    } else if (typeof toState.redirectMap[error] === 'object') {
                        redirectObj = toState.redirectMap[error];
                        return $state.go(redirectObj.state, {error: redirectObj.prefix + error}, {
                            location: false,
                            inherit: false
                        });
                    }
                }
                return $state.go(AuthService.errorState, {error: error}, {location: false, inherit: false});
            });
            // Hook success
            $rootScope.$on('$stateChangeSuccess',
                function (event, toState, toParams, fromState, fromParams) {
                    // display new view from top
                    $window.scrollTo(0, 0);
                    // Save the route title
                    $rootScope.currTitle = $state.current.title;
                });

            $rootScope.currTitle = $state.current.title;
            $rootScope.pageTitle = function () {
                var title = $rootScope.app.name + ' - ' + ($rootScope.currTitle || $rootScope.app.description);
                document.title = title;
                return title;
            };

            // iPad may presents ghost click issues
            // if( ! browser.ipad )
            // FastClick.attach(document.body);

            // Close submenu when sidebar change from collapsed to normal
            $rootScope.$watch('app.layout.isCollapsed', function (newValue, oldValue) {
                if (newValue === false)
                    $rootScope.$broadcast('closeSidebarMenu');
            });

            // Restore layout settings
            if (angular.isDefined($localStorage.layout))
                $scope.app.layout = $localStorage.layout;
            else
                $localStorage.layout = $scope.app.layout;

            $rootScope.$watch("app.layout", function () {
                $localStorage.layout = $scope.app.layout;
            }, true);


            // Allows to use branding color with interpolation
            // {{ colorByName('primary') }}
            $scope.colorByName = colors.byName;

            // Hides/show user avatar on sidebar
            $scope.toggleUserBlock = function () {
                $scope.$broadcast('toggleUserBlock');
            };

            // Internationalization
            // ----------------------

            $scope.language = {
                // list of available languages
                available: {
                    'en-GB': {name: 'English', iconid: "gb"},
                    'pt-PT': {name: 'Português', iconid: "pt"}
                },
                // display always the current ui language
                init: function () {
                    var proposedLanguage = $translate.proposedLanguage() || $translate.use();
                    var preferredLanguage = $translate.preferredLanguage(); // we know we have set a preferred one in app.config
                    var localeId = (proposedLanguage || preferredLanguage);
                    var lang = $scope.language.available[localeId];
                    $scope.language.selected = {localeId: localeId, name: lang.name, iconid: lang.iconid};
                },
                set: function (localeId, ev) {
                    // Set the new idiom
                    $translate.use(localeId);
                    // save a reference for the current language
                    var lang = $scope.language.available[localeId];
                    $scope.language.selected = {localeId: localeId, name: lang.name, iconid: lang.iconid};
                }
            };

            $scope.language.init();

            // Restore application classes state
            toggle.restoreState($(document.body));

            // cancel click event easily
            $rootScope.cancel = function ($event) {
                $event.stopPropagation();
            };
        }]);
