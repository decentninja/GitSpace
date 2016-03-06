angular.module('gitSpace.filters', [])
/*
* Show nice activity threshold time filter
*/
.filter('activityThresholdTime', function() {
  // We recieve hours
  return function(input) {
    var hours = input;
    var days = Math.floor(hours/24);
    hours = hours - days*24;
    var weeks = Math.floor(days/7);
    var output = " ";
    if(weeks > 0) {
      output += weeks + " week";
      return output;
    }
    if(days > 0) {
      output += days + " day";
      if(days > 1) { output += "s"; }
    }
    if(hours > 0) {
      if(days > 0) {
        output += ", ";
      }
      output += hours + " hour";
      if(hours > 1) { output += "s"; }
    }
    return output;
  };
});
