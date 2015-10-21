/*!
 *
 * Angle - Bootstrap Admin App + AngularJS
 *
 * Author: @themicon_co
 * Website: http://themicon.co
 * License: http://support.wrapbootstrap.com/knowledge_base/topics/usage-licenses
 *
 */

if (typeof $ === 'undefined') {
    throw new Error('This application\'s JavaScript requires jQuery');
}


// APP START
// ----------------------------------- 

var App = angular.module('dashboard', ['ngRoute', 'ngAnimate', 'ngStorage', 'ngCookies', 'pascalprecht.translate', 'ui.bootstrap', 'ui.router', 'oc.lazyLoad', 'cfp.loadingBar', 'ngSanitize', 'ngResource', 'ui.utils'])
    .run(["$rootScope", "$state", "$stateParams", '$window', '$templateCache', '$filter', 'AuthService', function ($rootScope, $state, $stateParams, $window, $templateCache, $filter, AuthService) {
        // Set reference to access them from any scope
        $rootScope.$state = $state;
        $rootScope.$stateParams = $stateParams;
        $rootScope.$storage = $window.localStorage;

        // Uncomment this to disable template cache
        /*$rootScope.$on('$stateChangeStart', function(event, toState, toParams, fromState, fromParams) {
         if (typeof(toState) !== 'undefined'){
         $templateCache.remove(toState.templateUrl);
         }
         });*/

        $rootScope.previousState = {};
        $rootScope.$on('$stateChangeSuccess', function (event, toState, toStateParams, fromState, fromStateParams) {
            $rootScope.previousState = {name: fromState.name, params: fromStateParams};
        });

        // Scope Globals
        // -----------------------------------
        $rootScope.app = {
            name: 'Dashboard',
            description: 'Dashboard Web Application',
            year: ((new Date()).getFullYear()),
            layout: {
                isFixed: true,
                isCollapsed: false,
                isBoxed: false,
                isRTL: false,
                horizontal: false,
                isFloat: false,
                asideHover: false
            },
            useFullLayout: false,
            hiddenFooter: false,
            viewAnimation: 'ng-fadeInUp'
        };
        //$rootScope.user = {
        //  name: 'John',
        //  job: 'ng-Dev',
        //  picture: 'app/img/user/02.jpg'
        //};
        $rootScope.user = {};
        $rootScope.AuthService = AuthService;
        AuthService.init();

        $rootScope.toPrettyJSON = function (object, spacing) {
            return $filter('json')(object, spacing);
        };

        $rootScope.toPrettyXML = function (xml) {
            return formatXml(xml);
        };

    }]);
