/*
* Routing
*/
app.config(['$stateProvider', '$urlRouterProvider', function($stateProvider, $urlRouterProvider) {

  $stateProvider.state('app', {
    url: '/',
    abstract: true,
    templateUrl: 'views/app.html'
  })
  .state('app.start', {
    url: '',
    views: {
      'appContent' :{
        templateUrl: 'views/start.html',
        controller : "mainCtrl"
      }
    }
  })
  .state('app.settings', {
    url: 'settings',
    views: {
      'appContent' :{
        templateUrl: 'views/settings.html',
        controller : "settingsCtrl"
      }
    }
  });

  $urlRouterProvider.otherwise('/');

}]);
