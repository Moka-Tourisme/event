odoo.define('event.EventPortalSidebar', function (require) {
    'use strict';

    const dom = require('web.dom');
    var publicWidget = require('web.public.widget');
    var PortalSidebar = require('portal.PortalSidebar');
    var utils = require('web.utils');

    publicWidget.registry.EventPortalSidebar = PortalSidebar.extend({
        selector: '.o_portal_event_sidebar',
        events: {
            'click .o_portal_event_print': '_onPrintInvoice',
        },

        /**
         * @override
         */
        start: function () {
            var def = this._super.apply(this, arguments);

            var $eventHtml = this.$el.find('iframe#event_html');
            var updateIframeSize = this._updateIframeSize.bind(this, $eventHtml);

            $(window).on('resize', updateIframeSize);

            var iframeDoc = $eventHtml[0].contentDocument;
            console.log($eventHtml[0].contentDocument);
            if (iframeDoc.readyState === 'complete') {
                updateIframeSize();
            } else {
                $eventHtml.on('load', updateIframeSize);
            }
            return def;
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * Called when the iframe is loaded or the window is resized on customer portal.
         * The goal is to expand the iframe height to display the full report without scrollbar.
         *
         * @private
         * @param {object} $el: the iframe
         */
        _updateIframeSize: function ($el) {
            // Set it to 0 first to handle the case where scrollHeight is too big for its content.
            // $el.height(1100);

            // scroll to the right place after iframe resize
            if (!utils.isValidAnchor(window.location.hash)) {
                return;
            }
            var $target = $(window.location.hash);
            if (!$target.length) {
                return;
            }
            dom.scrollTo($target[0], {duration: 0});
        },
        /**
         * @private
         * @param {MouseEvent} ev
         */
        _onPrintInvoice: function (ev) {
            ev.preventDefault();
            var href = $(ev.currentTarget).attr('href');
            this._printIframeContent(href);
        },
    });
});
