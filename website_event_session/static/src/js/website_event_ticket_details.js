/*
    Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
    @author Iván Todorovich <ivan.todorovich@camptocamp.com>
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
odoo.define("website_event_session.ticket_details", function (require) {
    "use strict";

    const EventTicketsDetailWidget = require("website_event.ticket_details");

    EventTicketsDetailWidget.include({
        /**
         * @override
         */
        start() {
            const res = this._super.apply(this, arguments);
            this.$sessionId = this.$el.find("input[name='event_session_id']");
            this.useSessions = this.$sessionId.length;
            return res;
        },
        /**
         * @override
         */
        _onTicketQuantityChange() {
            const res = this._super.apply(this, arguments);
            if (this.useSessions) {
                const sessionId = parseInt(this.$sessionId.val());
                if (!sessionId) {
                    this.$("button.btn-primary").attr("disabled", true);
                }
            }
            return res;
        },
    });

    return EventTicketsDetailWidget;
});
