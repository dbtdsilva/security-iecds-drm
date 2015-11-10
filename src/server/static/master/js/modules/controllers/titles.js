App.controller('TitlesController', ['$route', '$rootScope', '$scope', '$http', function($route, $rootScope, $scope, $http) {
	$scope.titles = [];

	$rootScope.$watch('user.loggedIn', function(newValue, oldValue) {
		if (oldValue == false && newValue == true) {
			$route.reload();
		}

	});

	if ($rootScope.user.loggedIn) {
		$http.get("api/title/user/all", {}).then(
			function(response) {
				$scope.titles = response.data;
			},
			function(response) {
				console.log("Failed to load titles");
		});
	} else {
		$http.get("api/title/all", {}).then(
			function(response) {
				$scope.titles = response.data;
			},
			function(response) {
				console.log("Failed to load titles");
		});
	}
}]);