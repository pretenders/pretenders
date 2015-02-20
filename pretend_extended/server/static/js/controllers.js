'use strict';

/* Controllers */


function MockListCtrl($scope, $route, $routeParams, Mock) {
    console.log($routeParams);
    $scope.name = $routeParams['protocol'];
    $scope.mocks = Mock.query({'protocol': $scope.name});
    $scope.mock = Mock.get($routeParams);
}
