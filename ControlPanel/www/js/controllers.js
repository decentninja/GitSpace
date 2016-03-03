angular.module('starter.controllers', [])

.controller("mainCtrl", ['$scope', '$rootScope', 'Repositories', function($scope, $rootScope, Repositories) {

	$scope.repositories = Repositories.all();

	$rootScope.$on("dataAvailable", function(data) {
		$scope.repositories = Repositories.all();
		console.log("repositories loaded");
		console.log($scope.repositories);
		$scope.$apply();
	});
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
