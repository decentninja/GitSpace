angular.module('gitSpace.controllers', [])

.controller("mainCtrl", ['$scope', '$rootScope', 'Repositories', '$ionicModal', 'settings', '$state', function($scope, $rootScope, Repositories, $ionicModal, settings, $state) {

	if($rootScope.rootScope.loggedIn === false) {
		$state.go("app.login");
	}

	$scope.repositories = Repositories.all();
	$scope.rewindThreshold = 0;
	$scope.activityThreshold = 12;
	$scope.usersActivity = false;
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
		} else {
			// We are closing a repo
			Repositories.emit({
				command: 'reset camera',
				repo: repository.name
			});
			repository.show = false;
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

	$scope.rewind = function(rewind, userData, repository) {
		var minutes = rewind * 60; // We recieve hours
		if(minutes === 0) {
			console.log("Set realtime!");
		} else {
			console.log("Rewind", minutes, "minutes");
		}
		/*Repositories.emit({
			command: 'rewind',
			minutes: minutes,
			repo: repository.name,
			username: userData.username
	});*/
	};

	/*$scope.resetRewind = function(userData, repository) {
		Repositories.emit({
			command: 'rewind reset',
			repo: repository.name,
			username: userData.username
		});
	};*/

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
	Repositories.emit({
		command: 'repo add',
		repo: repository.owner + "/" + repository.repo
	});
	$scope.modal.hide();
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
*	Settings controller
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

}])

/*
*	Login controller
*/
.controller("login", ['$scope', '$rootScope', 'settings', '$state', '$ionicNavBarDelegate', function($scope, $rootScope, settings, $state, $ionicNavBarDelegate) {
	$ionicNavBarDelegate.showBackButton(false);

	if($rootScope.rootScope.loggedIn === true) {
		$state.go("app.start");
	}

	$scope.login = function() {
		window.open("https://github.com/login/oauth/authorize?client_id=7c7d1017c8a91f87d6f7", "_blank");
	};
}]);
