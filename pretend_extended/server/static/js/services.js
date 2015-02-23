// global angular 
'use strict';

/* Services */


angular.module('pretenders.history', ['ngResource'])
    .factory('History', function ($resource) {
        var History = $resource(
            '/history/:name',
            {},
            {}
        );

        return History;
    });

angular.module('pretenders.preset', ['ngResource'])
    .factory('Preset', function ($resource) {
        var Preset = $resource(
            '/preset/:name',
            {},
            {}
        );

        return Preset;
    });


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('pretenders.services', ['ngResource'])
    .value('version', '0.1')
    .factory('Mock', function ($resource, History, Preset) {
        var Mock = $resource(
            '/:protocol/:mock_id',
            {},
            {}
        );
        var history = null;
        var presets = null;

        Mock.prototype.get_history = function () {
            if (!this.history && this.name) {
                this.history = History.query({'name': this.name});
            }
            return this.history;
        };

        Mock.prototype.get_presets = function () {
            if (!this.presets && this.name) {
                this.presets = Preset.query({'name': this.name});
            }
            return this.presets;
        };

        Mock.prototype.keep_alive = function () {

        };

        return Mock;
    });
