App.controller('TitlesController', ['$scope', '$http', function($scope, $http) {
	$scope.titles = [];
    $http.get("api/title/all", {}).then(
    function(response) {
		$scope.titles = response.data;
	}, 
	function(response) {
        console.log("Failed to load titles");
	});	
}]);