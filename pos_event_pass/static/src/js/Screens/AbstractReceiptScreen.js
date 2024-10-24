/*
    Copyright 2023 Camptocamp SA (https://www.camptocamp.com).
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
odoo.define("pos_event_pass.AbstractReceiptScreen", function (require) {
    "use strict";

    const AbstractReceiptScreen = require("point_of_sale.AbstractReceiptScreen");
    const Registries = require("point_of_sale.Registries");

    /* eslint-disable no-shadow */
    const PosEventPassAbstractReceiptScreen = (AbstractReceiptScreen) =>
        class extends AbstractReceiptScreen {
            /**
             * Prints the event registration receipts through the printer proxy.
             * Doesn't do anything if there's no proxy printer.
             *
             * @returns {Boolean}
             */
            async _printEventPass() {
                // Check if in pos.config the option to print the event pass is enabled
                console.warn("this.env.pos.config.iface_print_pass ICI", this.env.pos.config.iface_print_pass);
                if (this.env.pos.proxy.printer && this.env.pos.config.iface_print_pass) {
                    const $receipts = this.el.getElementsByClassName(
                        "event-pass-receipt"
                    );
                    for (const $receipt of $receipts) {
                        const printResult =
                            await this.env.pos.proxy.printer.print_receipt(
                                $receipt.outerHTML
                            );
                        if (!printResult.successful) {
                            console.error("Unable to print event pass receipt");
                            console.debug(printResult);
                            return false;
                        }
                    }
                    return true;
                }
                return false;
            }
        };

    Registries.Component.extend(
        AbstractReceiptScreen,
        PosEventPassAbstractReceiptScreen
    );
    return AbstractReceiptScreen;
});
