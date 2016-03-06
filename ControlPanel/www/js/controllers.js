angular.module('gitSpace.controllers', [])

.controller("mainCtrl", ['$scope', '$rootScope', 'Repositories', function($scope, $rootScope, Repositories) {

	$scope.repositories = Repositories.all();

	$rootScope.$on("dataAvailable", function() {
		$scope.repositories = Repositories.all();
		console.log("Repositories loaded!");
		$scope.$apply();
	});

	$scope.zoomRepository = function(repository) {
		Repositories.emit('repo focus', {
			command: 'repo focus',
			repo: repository.name
		});
	};

}])

/*
*	Repository controller
*/
.controller("repositoryCtrl", ['$scope', '$stateParams', '$rootScope', 'Repositories', '$timeout', function($scope, $stateParams, $rootScope, Repositories, $timeout) {

	$scope.repository = Repositories.byName($stateParams.name);
	$scope.initialized = ($scope.repository !== null) ? true : false;
	$scope.rewindDays = 0;
	$scope.activityThreshold = 12;
	$scope.visuals = {
		labels: false
	};

	$rootScope.$on("dataAvailable", function() {
		console.log("Repositories loaded!");
		$scope.repository = Repositories.byName($stateParams.name);
		$scope.initialized = true;
		$scope.$apply();
	});

	$scope.setActivityThreshold = function(newActivityThreshold) {
		var minutes = newActivityThreshold * 60; // We recieve hours
		Repositories.emit("activity threshold", {
			command: 'activity threshold',
			threshold: minutes
		});
	};

	$scope.setLabels = function(bool) {
		Repositories.emit("labels", {
			command: 'labels',
			show: bool
		});
	};

	$scope.setUserActivity = function(userData) {
		Repositories.emit('user activity', {
			command: 'user activity',
			name: userData.name,
			mail: userData.mail
		});
	};

}]);
