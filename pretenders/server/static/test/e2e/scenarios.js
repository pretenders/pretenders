// global describe, beforeEach, it, expect, browser
'use strict';

/* http://docs.angularjs.org/guide/dev_guide.e2e-testing */

describe('my app', function () {

    beforeEach(function () {
        browser().navigateTo('/');
    });


    it('should redirect to /features when location fragment is empty', function () {
        browser().navigateTo('/');
        expect(browser().location().url()).toBe("/features");
    });

});
