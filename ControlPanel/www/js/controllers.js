angular.module('starter.controllers', [])

.controller("mainCtrl", ['$scope', 'Repositories', function($scope, Repositories) {

	$scope.repositories = Repositories.all();
}])

/*
*	Repository controller
*/
.controller("repositoryCtrl", ['$scope', '$stateParams', 'Repositories', '$timeout', function($scope, $stateParams, Repositories, $timeout) {

	$scope.repository = Repositories.byId($stateParams.id);
	$scope.totalDuration = 100; // In days
	$scope.rewindDays = 0;
	$scope.intensityDuration = 7;
	$scope.lightning = false;

	$scope.rewindNumberOfDays = function(days) {
		$scope.rewindDays = days;
		console.log($scope.rewindDays);
	}

	$scope.triggerLightning = function() {
		console.log("THUNDER!");
		$scope.lightning = true;
		$timeout(function() {
			$scope.lightning = false;
		}, 750);
	}

}]);