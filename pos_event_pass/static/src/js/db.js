/*
    Copyright 2021 Camptocamp (https://www.camptocamp.com).
    @author Iván Todorovich <ivan.todorovich@camptocamp.com>
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
odoo.define("pos_event_pass.db", function (require) {
    "use strict";

    const PosDB = require("point_of_sale.DB");
    const rpc = require("web.rpc");
    const {_t} = require("web.core");

    PosDB.include({
        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            this.pass_ticket_by_id = {};
        },
        /**
         * @param {Number|Array} ticket_id
         * @param {Boolean} raiseIfNotFound
         * @returns the pass ticket or list of pass tickets if you pass a list of ids.
         */
        getPassTicketByID: function (ticket_id, raiseIfNotFound = true) {
            if (ticket_id instanceof Array) {
                return ticket_id
                    .map((id) => this.getPassTicketByID(id, raiseIfNotFound))
                    .filter(Boolean);
            }
            const ticket = this.pass_ticket_by_id[ticket_id];
            if (!ticket && raiseIfNotFound) {
                throw new Error(
                    _.str.sprintf(_t("Event Ticket not found: %d"), ticket_id)
                );
            }
            return ticket;
        },
        
    });

    return PosDB;
});
