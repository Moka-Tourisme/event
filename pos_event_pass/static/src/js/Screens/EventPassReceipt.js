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
            console.log("ICI LE RECEIPT");
            this._receiptEnv = this.props.order.getOrderReceiptEnv();
        }

        willUpdateProps(nextProps) {
            this._receiptEnv = nextProps.order.getOrderReceiptEnv();
        }

        get receiptEnv() {
            console.log("this._receiptEnv", this._receiptEnv);
            return this._receiptEnv;
        }

        get receipt() {
            console.log("this.receiptEnv", this.receiptEnv);
            return this.receiptEnv.receipt;
        }

        get pass() {
            console.log("this.props.pass", this.props.pass);
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

        // get location() {
        //     data = this.rpc({
        //         model: "res.partner",
        //         method: "search",
        //         domain: [
        //             ["id", "in", this.props.location_id[0]],
        //         ],
        //         kwargs: {context: session.user_context},
        //     });
        //     console.log(data)
        //     return data;
        // }
    }

    EventPassReceipt.template = "EventPassReceipt";

    Registries.Component.add(EventPassReceipt);
    return EventPassReceipt;
});
