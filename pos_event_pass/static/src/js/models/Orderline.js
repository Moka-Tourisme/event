/*
    Copyright 2021 Camptocamp (https://www.camptocamp.com).
    @author Iván Todorovich <ivan.todorovich@camptocamp.com>
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
odoo.define("pos_event_pass.Orderline", function (require) {
    "use strict";

    const models = require("point_of_sale.models");
    const utils = require("web.utils");
    const core = require("web.core");
    const Registries = require("point_of_sale.Registries");
    const {Orderline} = require("point_of_sale.models");
    const _t = core._t;
    const round_di = utils.round_decimals;

    const PosEventPassOrderLine = (Orderline) => 
        
        class extends Orderline{
        /**
         * @returns the event.ticket object
         */
        getPassTicket() {
            if (this.pass_id) {
                return this.pos.db.getPassTicketByID(this.pass_id);
            }
        }

        /**
         * @override
         */
        clone() {
            const res = super.clone.apply(this, arguments);
            res.pass_type_id = this.pass_type_id;
            return res;
        }
        /**
         * @override
         */
        init_from_JSON(json) {
            super.init_from_JSON.apply(this, arguments);
            this.pass_type_id = json.product_id.pass_type_id;
        }
        /**
         * @override
         */
        export_as_JSON() {
            var res = super.export_as_JSON.apply(this, arguments);
            res.pass_type_id = this.pass_type_id;
            return res;
        }
        /**
         * @override
         */
        export_for_printing() {
            const res = super.export_for_printing.apply(this, arguments);
            if (this.pass_id) {
                res.pass_ticket = this.getPassTicket();
            }
            return res;
        }
    }

    return models;
});
