/*
Copyright 2021 Camptocamp (https://www.camptocamp.com).
@author Iván Todorovich <ivan.todorovich@camptocamp.com>
License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
odoo.define("pos_event_pass.EventPassTicket", function (require) {
    "use strict";

    const models = require("point_of_sale.models");

    models.EventPassTicket = window.Backbone.Model.extend({
        initialize: function (attr, options) {
            _.extend(this, options);
        },
        _prepareOrderlineOptions() {
            return {
                extras: {
                    pass_id: this.id,
                },
            };
        },
        /**
         * Computes the total ordered quantity for this event ticket.
         *
         * @param {Object} options
         * @param {Order} options.order defaults to the current order
         * @returns {Number} ordered quantity
         */
        getOrderedQuantity: function ({order} = {}) {
            /* eslint-disable no-param-reassign */
            order = order ? order : this.pos.get_order();
            if (!order) {
                return 0;
            }
            return order
                .get_orderlines()
                .filter((line) => line.getPassTicket() === this)
                .reduce((sum, line) => sum + line.quantity, 0);
        },
    });

    return models;
});
