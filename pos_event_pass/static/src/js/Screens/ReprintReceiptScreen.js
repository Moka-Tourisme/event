/*
    Copyright 2023 Camptocamp (https://www.camptocamp.com).
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
odoo.define("pos_event_pass.ReprintReceiptScreen", function (require) {
    "use strict";

    const ReprintReceiptScreen = require("point_of_sale.ReprintReceiptScreen");
    const Registries = require("point_of_sale.Registries");
    const session = require("web.session");

    /* eslint-disable no-shadow */
    const PosEventPassReprintReceiptScreen = (ReprintReceiptScreen) =>
        class extends ReprintReceiptScreen {
            /**
             * @override
             */
            async willStart() {
                await super.willStart();
                const order = this.props.order;
                if (order.backendId) {
                    order.event_pass = await this.rpc({
                        model: "event.pass.line",
                        method: "search_read",
                        domain: [
                            ["pos_order_id", "=", order.backendId],
                        ],
                        kwargs: {context: session.user_context},
                    });
                }
            }

            /**
             * @override
             */
            async _printReceipt() {
                const res = await super._printReceipt();
                await this._printEventPass();
                return res;
            }
        };

    Registries.Component.extend(ReprintReceiptScreen, PosEventPassReprintReceiptScreen);
    return ReprintReceiptScreen;
});
