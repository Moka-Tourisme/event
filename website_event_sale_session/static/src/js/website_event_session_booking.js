/*
    Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
    @author Iván Todorovich <ivan.todorovich@camptocamp.com>
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
odoo.define("website_event_sale_session.booking", function (require) {
    "use strict";

    const WebsiteEventSessionBooking = require("website_event_session.booking");
    const {Markup} = require("web.utils");

    WebsiteEventSessionBooking.include({
        xmlDependencies: WebsiteEventSessionBooking.prototype.xmlDependencies.concat([
            "/website_event_sale_session/static/src/xml/website_event_session_booking.xml",
        ]),

        /**
         * @override
         */
        async _getSessionTickets() {
            const html_fields = ["price_html", "price_reduce_html"];
            const tickets = await this._super.apply(this, arguments);
            for (const ticket of tickets) {
                for (const field of html_fields) {
                    if (field in ticket) {
                        ticket[field] = Markup(ticket[field]);
                    }
                }
            }
            return tickets;
        },
    });

    return WebsiteEventSessionBooking;
});
