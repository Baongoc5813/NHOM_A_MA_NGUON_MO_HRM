odoo.define('smart_workload_balancer.workload_dashboard', function (require) {
    'use strict';

    var core = require('web.core');
    var Widget = require('web.Widget');

    var WorkloadDashboardWidget = Widget.extend({
        template: 'smart_workload_balancer.workload_dashboard',
        init: function (parent, options) {
            this._super.apply(this, arguments);
            this.options = options || {};
        },
    });

    return WorkloadDashboardWidget;
});
