/**=========================================================
 * Module: config.js
 * App routes and resources configuration
 =========================================================*/

App.config(['$stateProvider', '$httpProvider', '$locationProvider', '$urlRouterProvider', 'APP_REQUIRES', 'RouteHelpersProvider',
function ($stateProvider, $httpProvider, $locationProvider, $urlRouterProvider, appRequires, helper) {
  'use strict';
  //$httpProvider.defaults.headers.common["Accept-Language"] = "pt_PT, en;q=0.8, pt-PT;q=0.6";
  // Set the following to true to enable the HTML5 Mode pt-pt
  // You may have to set <base> tag in index and a routing configuration in your server
  $locationProvider.html5Mode(false);

  // default route
  //$urlRouterProvider.otherwise('/app/singleview');
  $urlRouterProvider.otherwise('/app/home');

  // 
  // Application Routes
  // -----------------------------------   
  $stateProvider
    .state('app', {
        url: '/app',
        abstract: true,
        templateUrl: helper.basepath('app.html'),
        controller: 'AppController',
        resolve: helper.resolveFor('localytics.directives', 'modernizr', 'slimscroll', 'icons',
                                    'ui.gravatar', 'hljs', 'toaster')
    })
    .state('app.home', {
        url: '/home',
        title: 'Home',
        templateUrl: helper.basepath('home.html'),
        controller: 'HomeController',
        resolve: helper.resolveFor('chart', 'localytics.directives', 'chart.js', 'angular-carousel'),
        accessLevel: 'public'
    })
    .state('app.about', {
        url: '/about',
        title: 'About',
        templateUrl: helper.basepath('partials/about.html'),
        //controller: 'HomeController',
        //resolve: helper.resolveFor('chart', 'paho-mqtt', 'localytics.directives', 'chart.js', 'angular-carousel'),
        accessLevel: 'public'
    })
    .state('app.titles', {
        url: '/titles',
        title: 'Titles',
        templateUrl: helper.basepath('partials/titles.html'),
        controller: 'TitlesController',
        resolve: helper.resolveFor('localytics.directives', 'angular-carousel'),
        accessLevel: 'public'
    }) 
    .state('app.error', {
        url: '/error/:error',
        title: 'Error',
        templateUrl: helper.basepath('error.html'),
        accessLevel: 'public'
    })
    //
    // Single Page Routes
    // -----------------------------------
    .state('page', {
        url: '/page',
        templateUrl: 'app/pages/page.html',
        resolve: helper.resolveFor('modernizr', 'icons', 'parsley'),
        accessLevel: 'public'
    })
    .state('page.login', {
        url: '/login',
        title: "Login",
        templateUrl: 'app/pages/login.html',
        accessLevel: 'public'
    })
    .state('page.must-login', {
        url: '/login/{detail}{status:int}',
        title: "Login",
        templateUrl: 'app/pages/login.html',
        accessLevel: 'public'
    })
    //.state('page.register', {
    //    url: '/register',
    //    title: "Register",
    //    templateUrl: 'app/pages/register.html',
    //    accessLevel: 'anon'
    //})
    //.state('page.recover', {
    //    url: '/recover',
    //    title: "Recover",
    //    templateUrl: 'app/pages/recover.html',
    //    accessLevel: 'anon'
    //})
    //.state('page.lock', {
    //    url: '/lock',
    //    title: "Lock",
    //    templateUrl: 'app/pages/lock.html',
    //    accessLevel: 'public'
    //})
    .state('page.404', {
        url: '/404',
        title: "Not Found",
        templateUrl: 'app/pages/404.html',
        accessLevel: 'public'
    })
    // 
    // CUSTOM RESOLVES
    //   Add your own resolves properties
    //   following this object extend
    //   method
    // ----------------------------------- 
    // .state('app.someroute', {
    //   url: '/some_url',
    //   templateUrl: 'path_to_template.html',
    //   controller: 'someController',
    //   resolve: angular.extend(
    //     helper.resolveFor(), {
    //     // YOUR RESOLVES GO HERE
    //     }
    //   )
    // })
    ;


}]).config(['$ocLazyLoadProvider', 'APP_REQUIRES', function ($ocLazyLoadProvider, APP_REQUIRES) {
    'use strict';

    // Lazy Load modules configuration
    $ocLazyLoadProvider.config({
      debug: false,
      events: true,
      modules: APP_REQUIRES.modules
    });

}]).config(['$controllerProvider', '$compileProvider', '$filterProvider', '$provide',
    function ( $controllerProvider, $compileProvider, $filterProvider, $provide) {
      'use strict';
      // registering components after bootstrap
      App.controller = $controllerProvider.register;
      App.directive  = $compileProvider.directive;
      App.filter     = $filterProvider.register;
      App.factory    = $provide.factory;
      App.service    = $provide.service;
      App.constant   = $provide.constant;
      App.value      = $provide.value;

}]).config(['$translateProvider', function ($translateProvider) {

    /*$translateProvider.useStaticFilesLoader({
        prefix : 'app/i18n/',
        suffix : '.json'
    });
    //$translateProvider.preferredLanguage('en-GB');
    $translateProvider.preferredLanguage('pt-PT');
    //$translateProvider.rememberLanguage(true);
    $translateProvider.useLocalStorage();
    $translateProvider.usePostCompiling(true);
    */
}]).config(['cfpLoadingBarProvider', function(cfpLoadingBarProvider) {
    cfpLoadingBarProvider.includeBar = true;
    cfpLoadingBarProvider.includeSpinner = false;
    cfpLoadingBarProvider.latencyThreshold = 500;
    //cfpLoadingBarProvider.parentSelector = '.wrapper > section';
}]).config(['$httpProvider', function($httpProvider) {
  // register the interceptor via an anonymous factory
  /*$httpProvider.interceptors.push(function($q, $location, $injector) {
    return {
      'responseError': function(response) {
        console.error('http interceptor', response.status, response.data.detail);
        // 401 {detail: 'Authentication credentials were not provided.'}
        // 401 {detail: 'Error decoding signature.'}
        // 401 {detail: 'Signature has expired.'}
        if (response.status === 401 && response.data.detail) {
          if (response.data.detail === 'Authentication credentials were not provided.' ||
              response.data.detail === 'Signature has expired.' ||
              response.data.detail === 'Invalid signature' ||
              response.data.detail === 'As credenciais de autenticação não foram fornecidas.' ||
              response.data.detail === 'Assinatura expirou.' ||
              response.data.detail === 'Assinatura inválida.') {
            $injector.get('$state').go('page.must-login', { detail: response.data.detail, status: response.status}, {location: false, inherit: false});
          }
        }
        if (response.status === 403 && response.data.detail) {
          if (response.data.detail === 'You do not have permission to perform this action.') {
            // TODO show some notification
          }
        }
        return $q.reject(response);
      }
    };
  });*/
}])
.controller('NullController', function() {});
