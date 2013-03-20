// global describe, beforeEach, inject, it, expect
// global FeatureListCtrl
'use strict';

/* jasmine specs for controllers go here */

describe('Http Mock list controller', function () {
    var scope, ctrl, $httpBackend;

    beforeEach(module('pretenders.services'));

    beforeEach(inject(function (_$httpBackend_, $rootScope, $controller) {
        $httpBackend = _$httpBackend_;
        $httpBackend
            .expectGET('/http')
            .respond([
                {
                    uid: '1',
                    name: 'first_mock'
                },
                {
                    uid: '2',
                    name: 'second_mock'
                }
            ]);

        scope = $rootScope.$new();
        ctrl = $controller(HttpMockListCtrl, {$scope: scope});
    }));


    it('should add features to the scope', function () {
        $httpBackend.flush();

        expect(scope.features.length).toBe(2);
        expect(scope.features[1].title).toBe('Second Feature');
    });
});
