// global angular
'use strict';

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('pretenders.services', ['ngResource'])
    .value('version', '0.1')
    .factory('Mock', function ($resource) {
        return $resource(
            '/:mocktype/:mockId',
            {},
            {
                query: {
                    method: 'GET',
                    params: {mockId: '',
                             mocktype: 'http'},
                    isArray: true
                }
            });
    });
