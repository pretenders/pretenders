'use strict';

/* Controllers */


function MockListCtrl($scope, $routeParams, Mock) {
    $scope.mocks = Mock.query({mocktype:$routeParams['type']});
    $scope.name = $routeParams['type'];
}
