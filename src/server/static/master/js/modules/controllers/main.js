/**=========================================================
 * Module: main.js
 * Main Application Controller
 =========================================================*/
App.controller('AppController',
    ['$rootScope', '$scope', '$state', '$translate', '$window', '$localStorage', '$timeout', '$location', '$http', 'toggleStateService', 'colors', 'browser', 'cfpLoadingBar', 'toaster',
        function ($rootScope, $scope, $state, $translate, $window, $localStorage, $timeout, $location, $http, toggle, colors, browser, cfpLoadingBar, toaster) {
            "use strict";


                


            /**************************************************
             ***************** APPLICATION ********************
             **************************************************/
                // Setup the layout mode
            $rootScope.app.layout.horizontal = ( $rootScope.$stateParams.layout == 'app-h');

            $rootScope.cfpLoadingBar = cfpLoadingBar;
            // Loading bar transition
            // -----------------------------------
            var thBar;
            $rootScope.$on('$stateChangeStart', function (event, toState, toParams, fromState, fromParams) {
                if ($('.wrapper > section').length) // check if bar container exists
                    thBar = $timeout(function () {
                        cfpLoadingBar.start();
                    }, 0); // sets a latency Threshold

            });
            $rootScope.$on('$stateChangeSuccess', function (event, toState, toParams, fromState, fromParams) {
                event.targetScope.$watch("$viewContentLoaded", function () {
                    $timeout.cancel(thBar);
                    cfpLoadingBar.complete();
                });
            });


            // Hook not found
            $rootScope.$on('$stateNotFound', function (event, unfoundState, fromState, fromParams) {
                console.log('$stateNotFound');
                console.log(unfoundState.to); // "lazy.state"
                console.log(unfoundState.toParams); // {a:1, b:2}
                console.log(unfoundState.options); // {inherit:false} + default options
            });
            // Hook error
            $rootScope.stateChangeErrorCout = 0;
            /**
             * Gets triggered when a resolve isn't fulfilled
             * NOTE: when the user doesn't have required permissions for a state, this event
             *       it's not triggered.
             *
             * In order to redirect to the desired state, the $http status code gets parsed.
             * If it's an HTTP code (ex: 403), could be prefixed with a string (ex: resolvename403),
             * to handle same status codes for different resolve(s).
             * This is defined inside $state.redirectMap.
             */
            // rootScope.$on('$stateChangeError', function (event, toState, toParams, fromState, fromParams, error) {
            //     console.log('$stateChangeError', error);
            //     $rootScope.stateChangeErrorCout++;
            //     if ($rootScope.stateChangeErrorCout > 4) return;
            //     //return $state.go(AuthService.errorState, { error: error }, { location: false, inherit: false });
            //     /**
            //      * This is a very clever way to implement failure redirection.
            //      * You can use the value of redirectMap, based on the value of the rejection
            //      * So you can setup DIFFERENT redirections based on different promise errors.
            //      */
            //     var redirectObj;
            //     // in case the promise given to resolve function is an $http request
            //     // the error is a object containing the error and additional informations
            //     error = (typeof error === 'object') ? error.status + '' : error;
            //     // in case of a random 4xx/5xx status code from server, user gets loggedout
            //     // otherwise it *might* forever loop (look call diagram)
            //     //if (/^[45]\d{2}$/.test(error)) {
            //     //    AuthService.logout();
            //     //}
            //     /**
            //      * Generic redirect handling.
            //      * If a state transition has been prevented and it's not one of the 2 above errors, means it's a
            //      * custom error in your application.
            //      *
            //      * redirectMap should be defined in the $state(s) that can generate transition errors.
            //      */
            //     if (angular.isDefined(toState.redirectMap) && angular.isDefined(toState.redirectMap[error])) {
            //         if (typeof toState.redirectMap[error] === 'string') {
            //             return $state.go(toState.redirectMap[error], {error: error}, {location: false, inherit: false});
            //         } else if (typeof toState.redirectMap[error] === 'object') {
            //             redirectObj = toState.redirectMap[error];
            //             return $state.go(redirectObj.state, {error: redirectObj.prefix + error}, {
            //                 location: false,
            //                 inherit: false
            //             });
            //         }
            //     }
            //     return $state.go(AuthService.errorState, {error: error}, {location: false, inherit: false});
            //});
            // Hook success
            $rootScope.$on('$stateChangeSuccess',
                function (event, toState, toParams, fromState, fromParams) {
                    // display new view from top
                    $window.scrollTo(0, 0);
                    // Save the route title
                    $rootScope.currTitle = $state.current.title;
                });

            $rootScope.currTitle = $state.current.title;
            $rootScope.pageTitle = function () {
                var title = $rootScope.app.name + ' - ' + ($rootScope.currTitle || $rootScope.app.description);
                document.title = title;
                return title;
            };

            // iPad may presents ghost click issues
            // if( ! browser.ipad )
            // FastClick.attach(document.body);

            // Close submenu when sidebar change from collapsed to normal
            $rootScope.$watch('app.layout.isCollapsed', function (newValue, oldValue) {
                if (newValue === false)
                    $rootScope.$broadcast('closeSidebarMenu');
            });

            // Restore layout settings
            if (angular.isDefined($localStorage.layout))
                $scope.app.layout = $localStorage.layout;
            else
                $localStorage.layout = $scope.app.layout;

            $rootScope.$watch("app.layout", function () {
                $localStorage.layout = $scope.app.layout;
            }, true);


            // Allows to use branding color with interpolation
            // {{ colorByName('primary') }}
            $scope.colorByName = colors.byName;

            // Hides/show user avatar on sidebar
            $scope.toggleUserBlock = function () {
                $scope.$broadcast('toggleUserBlock');
            };

            // Internationalization
            // ----------------------

            $scope.language = {
                // list of available languages
                available: {
                    'en-GB': {name: 'English', iconid: "gb"},
                    'pt-PT': {name: 'Português', iconid: "pt"}
                },
                // display always the current ui language
                init: function () {
                    var proposedLanguage = $translate.proposedLanguage() || $translate.use();
                    var preferredLanguage = $translate.preferredLanguage(); // we know we have set a preferred one in app.config
                    var localeId = (proposedLanguage || preferredLanguage);
                    var lang = $scope.language.available[localeId];
                    $scope.language.selected = {localeId: localeId, name: lang.name, iconid: lang.iconid};
                },
                set: function (localeId, ev) {
                    // Set the new idiom
                    $translate.use(localeId);
                    // save a reference for the current language
                    var lang = $scope.language.available[localeId];
                    $scope.language.selected = {localeId: localeId, name: lang.name, iconid: lang.iconid};
                }
            };

            $scope.language.init();

            // Restore application classes state
            toggle.restoreState($(document.body));

            // cancel click event easily
            $rootScope.cancel = function ($event) {
                $event.stopPropagation();
            };
        }]);
