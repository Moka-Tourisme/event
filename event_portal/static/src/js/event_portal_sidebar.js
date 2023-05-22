odoo.define('event.EventPortalSidebar', function (require) {
    'use strict';

    const dom = require('web.dom');
    var publicWidget = require('web.public.widget');
    var PortalSidebar = require('portal.PortalSidebar');
    var utils = require('web.utils');

    publicWidget.registry.EventPortalSidebar = PortalSidebar.extend({
        selector: '.o_portal_event_sidebar',
        events: {
            'click .o_portal_event_print': '_onPrintCustomerList',
        },

        /**
         * @private
         * @param {MouseEvent} ev
         */
        _onPrintCustomerList: function (ev) {
            ev.preventDefault();
            var href = $(ev.currentTarget).attr('href');
            this._printIframeContent(href);
        },
    });
});
