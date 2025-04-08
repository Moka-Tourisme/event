odoo.define('pos_event_pass.product_pass_type', function (require) {
    "use strict";
    const models = require('point_of_sale.models');
    const {Orderline} = require('point_of_sale.models');
    const Registries = require('point_of_sale.Registries');

    const PassType = (Orderline) =>
        class extends Orderline {
            initialize(attr, options) {
                super.initialize(attr, options);
                if (options && options.product && options.product.pass_type_id && options.product.pass_type_id.length > 0) {
                    this.pass_type_id = options.product.pass_type_id[0];
                } else {
                    this.pass_type_id = false;
                }
            }
        }

    Registries.Model.extend(Orderline, PassType);
    return Orderline;
});
