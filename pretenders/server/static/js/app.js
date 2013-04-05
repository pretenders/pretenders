// global angular, HttpMockListCtrl
'use strict';


// Declare app level module which depends on filters, and services
angular.module('pretenders', [
        'pretenders.filters',
        'pretenders.services',
        'pretenders.directives',
        'pretenders.history',
        'pretenders.preset'
    ])
.config(['$routeProvider', function ($routeProvider) {
        $routeProvider.
            when('/', {templateUrl: '/static/partials/home.html'}).
            when('/:protocol', {templateUrl: '/static/partials/mocks.html', controller: MockListCtrl }).
            when('/:protocol/:mock_id', {templateUrl: '/static/partials/mocks.html', controller: MockListCtrl });
            //when('/mocks/:mock/preset', {templateUrl:})
    }]
);


// TODO:
//  - Add history and preset sections to the page that are populated when a job
//    is clicked on. Use fake data to begin with.
//  - On each click of a job, fetch only what has changed since the last click.
//  - Add a "keep alive" button next to a mock server.
//
//  Think I want to somehow allocate a partial area to be history or params
//  and use  Mock.get($routeParams); on a click to populate it.
//  MockListCtrl should really be just the list control I guess...
//
