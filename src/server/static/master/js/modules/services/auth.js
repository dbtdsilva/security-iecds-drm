/**
 * Created by pmec on 23/12/14.
 */

/**=========================================================
 * Module: auth.js
 * Services to authenticate the client
 =========================================================*/

App.service('AuthService', ['$rootScope', '$http', '$window', '$q', function ($rootScope, $http, $window, $q) {

    var Auth = {
        deleteToken: deleteToken,
        getToken: getToken,
        hasToken: hasToken,
        setToken: setToken,
        getUser: getUser,
        setUser: setUser,
        deleteUser: deleteUser,
        init: init,
        login: login,
        logout: logout,
        me: me,
        resolvePendingState: resolvePendingState,
        canAccess: canAccess,
        /**
         * Public properties
         */
        userRole: null,
        user: {},
        token: {},
        isLogged: null,
        pendingStateChange: null,
        doneLoading: null,
        errorState: 'app.error',
        logoutState: 'app.home',
        loginState: 'page.login',
        homeState: 'app.home',
        response: null
    };

    return Auth;

    function deleteToken() {
        $window.localStorage.removeItem('jwt');
        $window.localStorage.removeItem('rft');
        delete $http.defaults.headers.common['Authorization'];
        Auth.token = {};
    }

    function getToken() {
        return {
            jwt: $window.localStorage.getItem('jwt'),
            rft: $window.localStorage.getItem('rft')
        };
    }

    function setToken(token) {
        if (!token) return;
        Auth.token = token;
        $rootScope.token = token;
        $window.localStorage.setItem('jwt', token.jwt);
        $window.localStorage.setItem('rft', token.rft);

        if (!!token.jwt)
            $http.defaults.headers.common['Authorization'] = 'JWT ' + token.jwt.toString();
    }

    function hasToken() {
        var token = getToken();
        return !!(token.jwt || token.rft);
    }

    function getUser() {
        return angular.fromJson($window.localStorage.getItem('user'));
    }

    function setUser(user) {
        return $window.localStorage.setItem('user', angular.toJson(user));
    }

    function deleteUser() {
        return $window.localStorage.removeItem('user');
    }

    function init() {
        if (!hasToken() || !Auth.user) {
            Auth.user = {};
            Auth.token = {};
            Auth.userRole = userRoles.public;
            Auth.isLogged = false;
            Auth.doneLoading = true;
        } else {
            var user = Auth.getUser();
            if (!user) return;
            Auth.user = user;
            Auth.userRole = userRoles[user.role];
            Auth.isLogged = true;
            Auth.doneLoading = true;

            Auth.token = Auth.getToken();
            if (!!Auth.token.jwt)
                $http.defaults.headers.common['Authorization'] = 'JWT ' + Auth.token.jwt.toString();

            $rootScope.token = Auth.token;
            angular.extend($rootScope.user, Auth.user);
        }
    }

    function login(username, password) {
        return $http.post('api/auth/login/', {
            username: username, password: password
        }).then(loginSuccessFn, loginErrorFn);

        function loginSuccessFn(response, status, headers, config) {
            Auth.response = response;
            if (!!response.data.token) {
                // setup token
                Auth.setToken(response.data.token);
                // update user
                angular.extend(Auth.user, response.data.user);
                angular.extend($rootScope.user, Auth.user);
                // flag true on isLogged
                Auth.isLogged = true;
                // update userRole
                Auth.userRole = userRoles[response.data.user.role];

                Auth.setUser(Auth.user);
                return response.data;
            } else {
                return $q.reject(response.data);
            }
        }

        function loginErrorFn(response, status, headers, config) {
            Auth.response = response;
            console.error(response.data);
            return $q.reject(response.data);
        }
    }

    function resolvePendingState(httpPromise) {
        var checkUser = $q.defer(),
            self = this,
            pendingState = self.pendingStateChange;

        // When the $http is done, we register the http result into loginHandler, `data` parameter goes into loginService.loginHandler
        httpPromise.success(function (response, status, headers, config) {
            Auth.response = response;
            // setup token
            Auth.setToken(response.data.token);
            // update user
            angular.extend(Auth.user, response.data.user);
            angular.extend($rootScope.user, Auth.user);
            // flag true on isLogged
            Auth.isLogged = true;
            // update userRole
            Auth.userRole = userRoles[response.data.user.role];

            Auth.setUser(Auth.user);
            return response;
        });

        httpPromise.then(
            function success(httpObj) {
                Auth.response = httpObj;
                self.doneLoading = true;
                // duplicated logic from $stateChangeStart, slightly different, now we surely have the userRole informations.
                if (pendingState.toState.accessLevel === undefined || pendingState.toState.accessLevel.bitMask & self.userRole.bitMask) {
                    checkUser.resolve();
                } else {
                    checkUser.reject('unauthorized');
                }
            },
            function reject(httpObj) {
                Auth.response = httpObj;
                checkUser.reject(httpObj.status + '');
            }
        );
        /**
         * I setted up the state change inside the promises success/error,
         * so i can safely assign pendingStateChange back to null.
         */
        self.pendingStateChange = null;
        return checkUser.promise;
    }

    function logout() {
        return $http.post('api/auth/logout/', {}).then(logoutSuccessFn, logoutErrorFn);

        function logoutSuccessFn(response, status, headers, config) {
            Auth.response = response;
            Auth.deleteToken();
            Auth.deleteUser();
            Auth.userRole = userRoles.public;
            Auth.user = {};
            Auth.isLogged = false;
            return response;
        }

        function logoutErrorFn(response, status, headers, config) {
            Auth.response = response;
            Auth.deleteToken();
            Auth.deleteUser();
            Auth.userRole = userRoles.public;
            Auth.user = {};
            Auth.isLogged = false;
            console.error(response);
            return $q.reject(response);
        }
    }

    function me() {
        return $http.get('api/auth/me/', {}).then(meSuccessFn, meErrorFn);

        function meSuccessFn(response, status, headers, config) {
            Auth.response = response;
            return response;
        }

        function meErrorFn(response, status, headers, config) {
            Auth.response = response;
            console.error(response);
            return $q.reject(response);
        }
    }

    function canAccess(accessLevelName) {
        var accessLevel = undefined;
        if (accessLevels.hasOwnProperty(accessLevelName))
            accessLevel = accessLevels[accessLevelName];
        return accessLevel === undefined || !!(accessLevel.bitMask & Auth.userRole.bitMask);
    }
}]);
