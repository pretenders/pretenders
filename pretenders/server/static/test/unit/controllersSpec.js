// global describe, beforeEach, inject, it, expect
// global FeatureListCtrl
'use strict';

/* jasmine specs for controllers go here */

describe('Feature list controller', function () {
    var scope, ctrl, $httpBackend;

    beforeEach(module('deploystream.services'));

    beforeEach(inject(function (_$httpBackend_, $rootScope, $controller) {
        $httpBackend = _$httpBackend_;
        $httpBackend
            .expectGET('/features')
            .respond([
                {
                    project: 'deploystream',
                    id: '1',
                    title: 'First Feature'
                },
                {
                    project: 'deploystream',
                    id: '2',
                    title: 'Second Feature'
                }
            ]);

        scope = $rootScope.$new();
        ctrl = $controller(FeatureListCtrl, {$scope: scope});
    }));


    it('should add features to the scope', function () {
        $httpBackend.flush();

        expect(scope.features.length).toBe(2);
        expect(scope.features[1].title).toBe('Second Feature');
    });
});
