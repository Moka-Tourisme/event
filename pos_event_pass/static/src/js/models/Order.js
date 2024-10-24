/*
    Copyright 2021 Camptocamp (https://www.camptocamp.com).
    @author Iván Todorovich <ivan.todorovich@camptocamp.com>
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
odoo.define("pos_event_pass.Order", function (require) {
    "use strict";

    const models = require("point_of_sale.models");
    const core = require("web.core");
    const _t = core._t;
    const {Order} = require("point_of_sale.models");
    const Registries = require("point_of_sale.Registries");

    const PosEventPassOrder = (Order) =>

        class extends Order {
            /**
             * @returns {Orderlines} linked to event tickets
             */
            getPassOrderlines() {
                const res = this.get_orderlines().filter((line) => line.pass_type_id);
                return res;
            }

            /**
             * @returns Array of {event.ticket} included in this order
             */
            getPassTickets() {
                const res = _.unique(
                    this.getPassOrderlines().map((line) => line.getPassTicket())
                );
                return res;
            }

            hasPass() {
                return this.getPassTickets().length > 0;
            }

            /**
             * @override
             */
            wait_for_push_order() {
                const res = super.wait_for_push_order.apply(this, arguments);
                return Boolean(res || this.hasPass());
            }

            /**
             * @override
             */
            export_for_printing() {
                const res = super.export_for_printing.apply(this, arguments);
                res.event_pass = this.event_pass;
                return res;
            }
        };


    Registries.Model.extend(Order, PosEventPassOrder);

    return Order;
});
