angular.module('gitSpace.controllers', [])

.controller("mainCtrl", ['$scope', '$rootScope', 'Repositories', '$ionicModal', 'settings', function($scope, $rootScope, Repositories, $ionicModal, settings) {

	$scope.repositories = Repositories.all();
	$scope.rewindDays = 0;
	$scope.activityThreshold = 12;
	$scope.visuals = {
		labels: false
	};

	$scope.newRepository = {
		repo: null,
		owner: null
	};
	$scope.modal = null;


	$rootScope.$on("dataAvailable", function() {
		$scope.repositories = Repositories.all();
		console.log("Repositories loaded!");
		console.log($scope.repositories);
		for(var i in $scope.repositories) {
			$scope.repositories[i].show = false;
		}
		$scope.$apply();
	});

	$rootScope.$on("websocketsError", function() {
		console.log("Recieved websocketsError...");
		$rootScope.rootScope.error = "Could not establish server connection...";
		$scope.$apply();
	});

	$scope.activeRepository = function(repository) {
		// Close all others
		for(var i in $scope.repositories) {
			if($scope.repositories[i] != repository) {
				$scope.repositories[i].show = false;
			}
		}
		if(!repository.show) {
			// We are focusing on a repo!
			repository.show = true;
		} else {
			// We are closing a repo
			repository.show = false;
		}
	};

	$scope.zoomRepository = function(repository) {
		console.log(repository);
		if(!repository.show) {
			// We are focusing on a repo!
			Repositories.emit({
				command: 'repo focus',
				repo: repository.name
			});
		} else {
			// We are closing a repo
			Repositories.emit({
				command: 'reset camera'
			});
		}
	};

	$scope.setActivityThreshold = function(newActivityThreshold) {
		var minutes = newActivityThreshold * 60; // We recieve hours
		Repositories.emit({
			command: 'activity threshold',
			threshold: minutes
		});
	};

	$scope.setLabels = function(bool) {
		Repositories.emit({
			command: 'labels',
			show: bool
		});
	};

	$scope.setUserActivity = function(userData) {
		Repositories.emit({
			command: 'user activity',
			name: userData.name,
			mail: userData.mail
		});
	};

	$ionicModal.fromTemplateUrl('views/add-modal.html', {
		scope: $scope,
		animation: 'slide-in-up'
	}).then(function(modal) {
		$scope.modal = modal;
	});
	$scope.openModal = function() {
		$scope.modal.show();
	};
	$scope.closeModal = function() {
		$scope.modal.hide();
	};
	//Cleanup the modal when we're done with it!
	$scope.$on('$destroy', function() {
		$scope.modal.remove();
	});

	$scope.addRepository = function(repository) {
		var sendRepo = repository.owner + "/" + repository.repo;
		Repositories.emit({
			command: 'repo add',
			repo: repository.owner + "/" + repository.repo
		});
		$scope.modal.hide();
		$scope.newRepository = {
			owner: null,
			repo: null
		};
	};

	$scope.removeRepository = function(repository) {
		var confirmDialog = confirm("Are you sure?");
		if(confirmDialog) {
			console.log("Remove", repository);
		}
	};

	$scope.reloadWebsockets = function() {
		Repositories.setUrl(settings.webSocketUrl);
	};
}])

/*
*	Repository controller
*/
.controller("settingsCtrl", ['$scope', '$rootScope', 'Repositories', 'settings', function($scope, $rootScope, Repositories, settings) {
	$scope.webSocketUrl = settings.webSocketUrl;

	$scope.setWebsocketUrl = function(url) {
		console.log("In controller. Settings websockets URL", url);
		Repositories.setUrl(url);
	};

}]);
