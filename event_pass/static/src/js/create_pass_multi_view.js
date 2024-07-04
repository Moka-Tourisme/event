odoo.define('event_pass.create_pass_multi_view', function (require) {
    "use strict";
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');
    var TreeButton = ListController.extend({
        buttons_template: 'EventPassListView.buttons',
        events: _.extend({}, ListController.prototype.events, {
            'click .o_wizard_create_pass_multi': '_OpenWizard',
        }),
        _OpenWizard: function () {
            var self = this;
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'wizard.pass.line',
                name: 'Create Pass',
                views: [[false, 'form']],
                target: 'new',
            });
        }
    });
    var PassLineListView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: TreeButton,
        }),
    });

    viewRegistry.add('event_pass_tree', PassLineListView);
});