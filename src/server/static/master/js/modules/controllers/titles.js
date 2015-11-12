App.controller('TitlesController', ['$route', '$rootScope', '$scope', '$http', function($route, $rootScope, $scope, $http) {
	$scope.titles = [];

	$rootScope.$watch('user.loggedIn', function(newValue, oldValue) {
		if (oldValue != newValue) {
			reloadPage();
		}
	});

	function reloadPage() {
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
	};


	$scope.buy = function(title_id) {
		$http.post("api/title/"+title_id, {}).then(
			function(response) {
				reloadPage();
			},
			function(data, status, headers, config) {
                    alert("Failed to login");
		});
	}

	reloadPage();
}]);