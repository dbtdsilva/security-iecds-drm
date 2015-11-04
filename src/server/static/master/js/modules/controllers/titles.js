App.controller('TitlesController', ['$scope', '$http', function($scope, $http) {
	$scope.titles = [];
    $http.get("http://localhost:8080/api/titles/", {}).then(
    function(response) {
		$scope.titles = response.data;
	}, 
	function(response) {
        console.log("Failed to load titles");
	});	
}]);