/*
    Copyright 2021 Camptocamp (https://www.camptocamp.com).
    @author Iván Todorovich <ivan.todorovich@camptocamp.com>
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
odoo.define("pos_event_pass.PaymentScreen", function (require) {
    "use strict";

    const PaymentScreen = require("point_of_sale.PaymentScreen");
    const Registries = require("point_of_sale.Registries");
    const session = require("web.session");

    const PosEventPassPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            async _postPushOrderResolve(order, server_ids) {
                console.warn('order', order);
                if (order) {
                    order.event_pass = await this.rpc({
                        model: "event.pass.line",
                        method: "search_read",
                        domain: [
                            ["pos_order_id", "in", server_ids],
                        ],
                        kwargs: {context: session.user_context},
                    });
                }
                console.warn('order after', order);
                if (order.event_pass) {
                    for (const line of order.event_pass) {
                    //     Update location_id to have all fields
                        const location_id = await this.rpc({
                            model: "res.partner",
                            method: "search_read",
                            domain: [
                                ["id", "=", line.location_id[0]],
                            ],
                            kwargs: {context: session.user_context},
                        });
                        line.location_id = location_id[0];
                    }
                }
                return super._postPushOrderResolve(order, server_ids);
            }
        };

    Registries.Component.extend(PaymentScreen, PosEventPassPaymentScreen);

    return PaymentScreen;
});
