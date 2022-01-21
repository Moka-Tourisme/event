/*
    Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
    @author Iván Todorovich <ivan.todorovich@camptocamp.com>
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
odoo.define("website_event_sale_session.booking", function (require) {
    "use strict";

    const WebsiteEventSessionBooking = require("website_event_session.booking");

    WebsiteEventSessionBooking.include({
        xmlDependencies: WebsiteEventSessionBooking.prototype.xmlDependencies.concat([
            "/website_event_sale_session/static/src/xml/website_event_session_booking.xml",
        ]),
    });

    return WebsiteEventSessionBooking;
});
