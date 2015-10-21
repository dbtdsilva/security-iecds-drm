/**
 * Created by pmec on 08/01/15.
 */

var globalVar = {};
function formatXml(xml) {
  if (typeof(xml) === 'undefined')
    return;
  var formatted = '';
  var reg = /(>)(<)(\/*)/g;
  xml = xml.replace(reg, '$1\r\n$2$3');
  var pad = 0;
  jQuery.each(xml.split('\r\n'), function(index, node) {
    var indent = 0;
    if (node.match( /.+<\/\w[^>]*>$/ )) {
      indent = 0;
    } else if (node.match( /^<\/\w/ )) {
      if (pad != 0) {
        pad -= 1;
      }
    } else if (node.match( /^<\w[^>]*[^\/]>.*$/ )) {
      indent = 1;
    } else {
      indent = 0;
    }

    var padding = '';
    for (var i = 0; i < pad; i++) {
      padding += '  ';
    }

    formatted += padding + node + '\r\n';
    pad += indent;
  });

  return formatted;
}
//Array.prototype.diff = function(a) {
//    return this.filter(function(i) {return a.indexOf(i) < 0;});
//};

function objArrayDiff(a1, a2, property) {
  if (!Array.isArray(a1))
    return a2;
  if (!a1.hasOwnProperty(property) && !a2.hasOwnProperty(property))
  var o1={}, o2={}, i1={}, i2={}, diff=[], i, len, k;
  for (i=0, len=a1.length; i<len; i++) {
    if (a1[i].hasOwnProperty(property)) {
      k = a1[i][property]+'';
      o1[k] = true;
      i1[k] = i;
    }
  }
  for (i=0, len=a2.length; i<len; i++) {
    if (a2[i].hasOwnProperty(property)) {
      k = a2[i][property]+'';
      o2[k] = true;
      i2[k] = i;
    }
  }
  for (k in o1) {
    if (!(k in o2)) {
      diff.push(a1[i1[k]]);
    }
  }
  for (k in o2) {
    if (!(k in o1)) {
      diff.push(a2[i2[k]]);
    }
  }
  return diff;
}

function removeFromArray(array, obj, property) {
  if (!Array.isArray(array) || !obj.hasOwnProperty(property))
    return;
  var i, len, k;
  var ok = obj[property];
  for (i=0, len=array.length; i<len; i++) {
    if (array[i].hasOwnProperty(property)) {
      k = array[i][property];
      if (ok === k) {
        break;
      }
    }
  }
  //var idx = array.indexOf(obj);
  if (i < len) {
    array.splice(i, 1);
  }
  return array;
}