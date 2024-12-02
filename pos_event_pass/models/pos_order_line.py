import datetime

from odoo import fields, models


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    generated_pass_ids = fields.One2many(
        "event.pass.line", "pos_order_line_id", string="Bought Pass"
    )

    pass_id = fields.Many2one(
        "event.pass.line", string="Event Pass",
        readonly=True,
    )

    pass_type_id = fields.Many2one(
        "event.pass.type",
        string="Pass Type",
    )

    def _create_pass(self):
        return self.env["event.pass.line"].create(
            [self._build_pass() for _ in range(int(self.qty))]
        )

    def _build_pass(self):
        val_validity_date = self.product_id.pass_type_id.validity_date or fields.Date.today()
        return {
            "display_name": self.product_id.pass_type_id.display_name,
            "product_id":self.product_id.id,
            "location_id": self.product_id.location_id.id,
            "partner_id": self.order_id.partner_id.id or None,
            "event_type_ids": self.product_id.pass_type_id.event_type_ids.ids,
            "category_ids": self.product_id.pass_type_id.category_ids.ids,
            "event_stage_ids": self.product_id.pass_type_id.event_stage_ids.ids,
            "event_ids": self.product_id.pass_type_id.event_ids.ids,
            "session_ids": self.product_id.pass_type_id.session_ids.ids,
            "unauthorized_session_ids": self.product_id.pass_type_id.unauthorized_session_ids.ids,
            "validity_date": self.product_id.pass_type_id.validity_date or fields.Date.today(),
            "expiration_date": val_validity_date + datetime.timedelta(
                days=self.product_id.pass_type_id.validity_period) if not self.product_id.pass_type_id.fixed_expiration_date and self.product_id.pass_type_id.validity_period else self.product_id.pass_type_id.expiration_date,
            "fixed_number_allowed_event": self.product_id.pass_type_id.fixed_number_allowed_event or False,
            "number_allowed_event": self.product_id.pass_type_id.number_allowed_event or 0,
            "number_visitors": self.product_id.pass_type_id.number_visitors or 0,
            "pos_order_line_id": self.id,
            "pass_type_id": self.product_id.pass_type_id.id,
        }

    def _export_for_ui(self, orderline):
        res = super(PosOrderLine, self)._export_for_ui(orderline)
        res["pass_id"] = orderline.pass_id.id
        res["generated_pass_ids"] = orderline.generated_pass_ids.ids
        return res