/**=========================================================
 * Module: access-login.js
 * Login api
 =========================================================*/

App.controller('LoginFormController', ['$rootScope', '$scope', '$http', '$state', 'AuthService', function ($rootScope, $scope, $http, $state, AuthService) {

    // bind here all data from the form
    $scope.account = {};
    // place the message if something goes wrong
    $scope.authMsg = '';

    $scope.login = function () {
        $scope.authMsg = '';

        AuthService.login($scope.account.username, $scope.account.password)
            .then(loginSuccessFn, loginErrorFn);
        function loginSuccessFn(data) {
            // assumes if ok, response is an object with some data, if not, a string with error
            // customize according to your api
            if (!data.token) {
                $scope.authMsg = 'pages.login.INCORRECT';
            } else {
                //if ($scope.account.remember)
                //$state.go(AuthService.homeState);
                console.log($rootScope.previousState.name);
                if ($rootScope.previousState.name !== "app.home") {
                    $state.go($rootScope.previousState.name, $rootScope.previousState.params);
                } else {
                    $state.go("app.devices.overview");
                }

            }
        }

        function loginErrorFn(data) {
            if (data.non_field_errors) {
                $scope.authMsg = data.non_field_errors[0];
            } else {
                $scope.authMsg = 'pages.login.SERVERREQUEST';
            }
        }
    };

    $scope.logout = function () {
        AuthService.logout()
            .then(logoutSuccessFn, logoutErrorFn);
        function logoutSuccessFn(data) {
            $state.go('app.home');
        }

        function logoutErrorFn(data) {
        }
    };
}]);