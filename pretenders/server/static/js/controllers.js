// global HttpMock
'use strict';

/* Controllers */


function HttpMockListCtrl($scope, HttpMock) {
    $scope.mocks = HttpMock.query();
}
//HttpMockListCtrl.$inject = [];
