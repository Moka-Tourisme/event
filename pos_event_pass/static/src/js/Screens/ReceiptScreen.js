/*
    Copyright 2021 Camptocamp (https://www.camptocamp.com).
    @author Iván Todorovich <ivan.todorovich@camptocamp.com>
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
odoo.define("pos_event_pass.ReceiptScreen", function (require) {
    "use strict";

    const ReceiptScreen = require("point_of_sale.ReceiptScreen");
    const Registries = require("point_of_sale.Registries");

    /* eslint-disable no-shadow */
    const PosEventPassReceiptScreen = (ReceiptScreen) =>
        class extends ReceiptScreen {
            /**
             * @override
             */
            async printReceipt() {
                const res = await super.printReceipt();
                console.warn('res', res);
                await this._printEventPass();
                return res;
            }
        };

    Registries.Component.extend(ReceiptScreen, PosEventPassReceiptScreen);
    return ReceiptScreen;
});
