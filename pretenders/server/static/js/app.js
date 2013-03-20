// global angular, HttpMockListCtrl
'use strict';


// Declare app level module which depends on filters, and services
angular.module('pretenders', [
        'pretenders.filters',
        'pretenders.services',
        'pretenders.directives'
    ])
.config(['$routeProvider', function ($routeProvider) {
        $routeProvider.when('/', {
            templateUrl: '/static/partials/home.html'
        });
        $routeProvider.when('/http', {
            templateUrl: '/static/partials/mocks.html',
            controller: HttpMockListCtrl
        });
        $routeProvider.when('/smtp', {
            templateUrl: '/static/partials/mocks.html',
            controller: SmtpMockListCtrl
        });
    }]
);
