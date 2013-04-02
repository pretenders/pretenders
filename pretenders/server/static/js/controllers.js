'use strict';

/* Controllers */


function MockListCtrl($scope, $route, $routeParams, Mock) {
    console.log($routeParams);
    $scope.mocks = Mock.query($routeParams);
    $scope.mock = null;
    $scope.name = $routeParams['protocol'];

    $scope.selectMock = function(mock) {
        $scope.mock = mock;
        // Get history and presets.
    };
}
