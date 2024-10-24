odoo.define('pos_event_pass.product_pass_type', function (require) {
    "use strict";
    const models = require('point_of_sale.models');
    const _super_orderline = models.Orderline.prototype;
    models.load_fields('product.product', ['pass_type_id']);
    models.Orderline = models.Orderline.extend({
        initialize: function (attr, options) {
            _super_orderline.initialize.apply(this, arguments);
            if (options && options.product && options.product.pass_type_id && options.product.pass_type_id.length > 0) {
                this.pass_type_id = options.product.pass_type_id[0];
            } else {
                this.pass_type_id = false;
            }
        }
    });
});
