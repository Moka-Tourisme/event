/*
    Copyright 2021 Camptocamp (https://www.camptocamp.com).
    @author Iván Todorovich <ivan.todorovich@camptocamp.com>
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
odoo.define("pos_event_pass.EventPassReceipt", function (require) {
    "use strict";

    const PosComponent = require("point_of_sale.PosComponent");
    const Registries = require("point_of_sale.Registries");

    class EventPassReceipt extends PosComponent {
        constructor() {
            super(...arguments);
            this._receiptEnv = this.props.order.getOrderReceiptEnv();
        }
        willUpdateProps(nextProps) {
            this._receiptEnv = nextProps.order.getOrderReceiptEnv();
        }
        get receiptEnv() {
            return this._receiptEnv;
        }
        get receipt() {
            return this.receiptEnv.receipt;
        }

        get pass() {
            return this.props.pass;
        }

        get passTicket() {
            const [pass_id] = this.pass.pass_id || [false];
            return pass_id
                ? this.env.pos.db.getPassTicketByID(pass_id)
                : undefined;
        }

        formatDate(date) {
            return moment(date).format("ll");
        }
    }
    EventPassReceipt.template = "EventPassReceipt";

    Registries.Component.add(EventPassReceipt);
    return EventPassReceipt;
});
