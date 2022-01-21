# Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _cart_find_product_line(self, product_id=None, line_id=None, **kwargs):
        lines = super()._cart_find_product_line(product_id, line_id, **kwargs)
        if line_id:
            return lines
        if self.env.context.get("event_session_id"):
            lines = lines.filtered_domain(
                [("event_session_id", "=", self.env.context.get("event_session_id"))]
            )
        return lines

    def _website_product_id_change(self, order_id, product_id, qty=0, **kwargs):
        res = super()._website_product_id_change(
            order_id, product_id, qty=qty, **kwargs
        )
        if self.env.context.get("event_session_id"):
            res["event_session_id"] = self.env.context.get("event_session_id")
        return res
