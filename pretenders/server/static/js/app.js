// global angular, HttpMockListCtrl
'use strict';


// Declare app level module which depends on filters, and services
angular.module('pretenders', [
        'pretenders.filters',
        'pretenders.services',
        'pretenders.directives'
    ])
.config(['$routeProvider', function ($routeProvider) {
        $routeProvider.
            when('/', {templateUrl: '/static/partials/home.html'}).
            when('/mocks', {templateUrl: '/static/partials/mocks.html', controller: MockListCtrl });
            //when('/mocks/:mock/history', {templateUrl:})
            //when('/mocks/:mock/preset', {templateUrl:})
    }]
);


// TODO:
//  - Add history and preset sections to the page that are populated when a job
//    is clicked on. Use fake data to begin with.
//  - On each click of a job, fetch only what has changed since the last click.
//  - Add a "keep alive" button next to a mock server.
