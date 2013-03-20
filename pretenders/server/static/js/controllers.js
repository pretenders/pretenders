// global HttpMock
'use strict';

/* Controllers */


function HttpMockListCtrl($scope, Mock) {
    $scope.mocks = Mock.query({mocktype:"http"});
    $scope.name = 'HTTP';
}

function SmtpMockListCtrl($scope, Mock) {
    $scope.mocks = Mock.query({mocktype:"smtp"});
    $scope.name = 'SMTP';
}

//HttpMockListCtrl.$inject = [];
