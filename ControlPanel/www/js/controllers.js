angular.module('gitSpace.controllers', [])

.controller("mainCtrl", ['$scope', '$rootScope', 'Repositories', function($scope, $rootScope, Repositories) {

	$scope.repositories = Repositories.all();
	$scope.rewindDays = 0;
	$scope.activityThreshold = 12;
	$scope.visuals = {
		labels: false
	};

	$rootScope.$on("dataAvailable", function() {
		$scope.repositories = Repositories.all();
		console.log("Repositories loaded!");
		console.log($scope.repositories);
		for(var i in $scope.repositories) {
			$scope.repositories[i].show = false;
		}
		$scope.$apply();
	});

	$scope.zoomRepository = function(repository) {
		// Close all others
		for(var i in $scope.repositories) {
			if($scope.repositories[i] != repository) {
				$scope.repositories[i].show = false;
			}
		}
		if(!repository.show) {
			// We are focusing on a repo!
			Repositories.emit('repo focus', JSON.stringify({
				command: 'repo focus',
				repo: repository.name
			}));
			repository.show = true;
		} else {
			// We are closing a repo
			Repositories.emit('overview', JSON.stringify({
				command: 'overview'
			}));
			repository.show = false;
		}
	};

	$scope.setActivityThreshold = function(newActivityThreshold) {
		var minutes = newActivityThreshold * 60; // We recieve hours
		Repositories.emit("activity threshold", JSON.stringify({
			command: 'activity threshold',
			threshold: minutes
		}));
	};

	$scope.setLabels = function(bool) {
		Repositories.emit("labels", {
			command: 'labels',
			show: bool
		});
	};

	$scope.setUserActivity = function(userData) {
		Repositories.emit('user activity', JSON.stringify({
			command: 'user activity',
			name: userData.name,
			mail: userData.mail
		}));
	};

}])

/*
*	Repository controller
*/
.controller("repositoryCtrl", ['$scope', '$stateParams', '$rootScope', 'Repositories', '$timeout', function($scope, $stateParams, $rootScope, Repositories, $timeout) {

	$scope.repository = Repositories.byName($stateParams.name);
	$scope.initialized = ($scope.repository !== null) ? true : false;

	$rootScope.$on("dataAvailable", function() {
		console.log("Repositories loaded!");
		$scope.repository = Repositories.byName($stateParams.name);
		$scope.initialized = true;
		$scope.$apply();
	});

}]);
