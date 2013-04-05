'use strict';

/* Services */


angular.module('pretenders.history', ['ngResource']).factory('History', function($resource){
        var History = $resource(
            '/history/:uid',
            {},
            {}
        );

        return History;
});

angular.module('pretenders.preset', ['ngResource']).factory('Preset', function($resource){
        var Preset = $resource(
            '/preset/:uid',
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
        var _history = null;
        var _presets = null;

        Mock.prototype.get_history = function() {
            if (!this._history && this.uid){
                this._history = History.query({'uid': this.uid});
            }
            return this._history;
        };

        Mock.prototype.get_presets = function() {
            if (!this._presets && this.uid){
                this._presets = Preset.query({'uid': this.uid});
            }
            return this._presets;
        };

        Mock.prototype.keep_alive = function() {

        };

        return Mock;
    });
