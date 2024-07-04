# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _build_gift_card(self):
        gift_card = super()._build_gift_card()
        gift_card['product_template_id'] = self.product_template_id.id
        gift_card['customer_id'] = self.order_partner_id.id
        return gift_card
