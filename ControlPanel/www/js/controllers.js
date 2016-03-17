angular.module('gitSpace.controllers', [])

.controller("mainCtrl", ['$scope', '$rootScope', 'Repositories', '$ionicModal', 'settings', function($scope, $rootScope, Repositories, $ionicModal, settings) {

	$scope.repositories = Repositories.all();
	$scope.rewindThreshold = 0;
	$scope.userRewindThreshold = 0;
	$scope.activityThreshold = 12;
	$scope.usersActivity = false;
	$scope.visuals = {
		labels: false
	};

	$scope.newRepository = {
		repo: null,
		owner: null
	};
	$scope.addModal = null;
	$scope.userModal = null;

	$scope.activeUser = null;
	$scope.currentRepository = null;



	$rootScope.$on("dataAvailable", function() {
		$scope.repositories = Repositories.all();
		console.log("Repositories loaded!");
		console.log($scope.repositories);
		for(var i in $scope.repositories) {
			$scope.repositories[i].show = false;
		}
		$rootScope.rootScope.isWaiting = false;
		$rootScope.rootScope.error = null;
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
			$scope.currentRepository = repository;
		} else {
			// We are closing a repo
			Repositories.emit({
				command: 'reset camera',
				repo: repository.name
			});
			repository.show = false;
			$scope.currentRepository = null;
		}
	};

	$scope.zoomRepository = function(repository) {
		console.log(repository);
		// We are focusing on a repo!
		Repositories.emit({
			command: 'repo focus',
			repo: repository.name
		});
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

	$scope.setUserActivity = function(userData, repository) {
		Repositories.emit({
			command: 'user activity',
			repo: repository.name,
			username: userData.username
		});
		$scope.usersActivity = true;
	};

	$scope.resetUserActivity = function(repository) {
		Repositories.emit({
			command: 'user activity reset',
			repo: repository.name,
		});
		$scope.usersActivity = false;
	};

	$scope.rewind = function(rewind, repository, user) {
		var minutes = rewind * 60; // We recieve hours
		var username = "";
		if(user !== null) {
			username = user.username;
		}
		if(minutes === 0) {
			console.log("Set realtime!");
		} else {
			console.log("Rewind", minutes, "minutes");
		}
		Repositories.emit({
			command: 'rewind',
			minutes: minutes,
			repo: repository.name,
			username: username
		});
	};

	$ionicModal.fromTemplateUrl('views/add-modal.html', {
		scope: $scope,
		animation: 'slide-in-up'
	}).then(function(modal) {
		$scope.addModal = modal;
	});
	$scope.openAddModal = function(user) {
		$scope.addModal.show();
	};
	$scope.closeAddModal = function() {
		$scope.addModal.hide();
	};
	// User modal
	$ionicModal.fromTemplateUrl('views/user-modal.html', {
		scope: $scope,
		animation: 'slide-in-up'
	}).then(function(modal) {
		$scope.userModal = modal;
	});
	$scope.openUserModal = function(user) {
		$scope.activeUser = user;
		$scope.userModal.show();
	};
	$scope.closeUserModal = function() {
		$scope.activeUser = null;
		$scope.userModal.hide();
	};
	//Cleanup the modal when we're done with it!
	$scope.$on('$destroy', function() {
		$scope.addModal.remove();
		$scope.userModal.remove();
	});

	$scope.addRepository = function(repository) {
		Repositories.emit({
			command: 'repo add',
			repo: repository.owner + "/" + repository.repo
		});
		$scope.addModal.hide();
		$scope.newRepository = {
			owner: null,
			repo: null
		};
		// Let us wait!
		$scope.setWaiting();
	};

	$scope.removeRepository = function(repository) {
		var confirmDialog = confirm("Are you sure?");
		if(confirmDialog) {
			Repositories.emit({
				command: 'repo delete',
				repo: repository.name
			});
		}
		// Let us wait!
		$scope.setWaiting();
	};

	$scope.reloadWebsockets = function() {
		Repositories.reloadWs();
	};

	$scope.setWaiting = function () {
		$rootScope.rootScope.isWaiting = true;
		setTimeout(function() {
			if($rootScope.rootScope.isWaiting) {
				$rootScope.rootScope.isWaiting = false;
				$rootScope.rootScope.error = "Could not get the data from the server. Try again!";
				$scope.$apply();
			}
		}, 15000);
	};
}])

/*
*	Repository controller
*/
.controller("settingsCtrl", ['$scope', '$rootScope', 'Repositories', 'settings', '$state', function($scope, $rootScope, Repositories, settings, $state) {
	$scope.webSocketIP = Repositories.getIP();
	$scope.webSocketPort = Repositories.getPort();

	$scope.setWebsocketUrl = function(ip, port) {
		var url = "ws://" + ip + ":" + port;
		console.log("In controller. Settings websockets URL", url);
		Repositories.setUrl(url);
		$state.go('app.start');
	};

}]);
