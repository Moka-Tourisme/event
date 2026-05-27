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
        pass_type = self.product_id._get_pass_type()
        if pass_type.validity_option == 'fixed':
            validity_date = pass_type.validity_date or fields.Date.today()
            expiration_date = pass_type.expiration_date
        else:
            validity_date = fields.Date.today()
            expiration_date = validity_date + datetime.timedelta(days=pass_type.validity_period) if pass_type.validity_period else False
        return {
            "display_name": pass_type.display_name,
            # "product_id":self.product_id.id,
            "location_id": self.product_id.location_id.id,
            "partner_id": self.order_id.partner_id.id or None,
            "event_type_ids": pass_type.event_type_ids.ids,
            "category_ids": pass_type.category_ids.ids,
            "event_stage_ids": pass_type.event_stage_ids.ids,
            "event_ids": pass_type.event_ids.ids,
            "session_ids": pass_type.session_ids.ids,
            "unauthorized_session_ids": pass_type.unauthorized_session_ids.ids,
            "validity_date": validity_date,
            "expiration_date": expiration_date,
            "fixed_number_allowed_event": pass_type.fixed_number_allowed_event,
            "number_allowed_event": pass_type.number_allowed_event,
            "fixed_number_visitors_allowed": pass_type.fixed_number_visitors_allowed,
            "number_visitors": pass_type.number_visitors,
            "pos_order_line_id": self.id,
            "pass_type_id": pass_type.id,
        }

    def _export_for_ui(self, orderline):
        res = super(PosOrderLine, self)._export_for_ui(orderline)
        res["pass_id"] = orderline.pass_id.id
        res["generated_pass_ids"] = orderline.generated_pass_ids.ids
        return res


    def _cancel_refunded_event_pass(self):
        """
        Cancel the event pass linked to the order line if the order is refunded.
        """
        for line in self:
            if not line.product_id.detailed_type == "pass" or not line.refunded_orderline_id:
                continue
            to_cancel_qty = max(0, -int(line.qty))
            open_passes = line.refunded_orderline_id.generated_pass_ids.filtered(
                lambda p: p.state in ["valid", "draft"]
            )
            to_cancel_passes = open_passes[-to_cancel_qty:]
            to_cancel_passes.action_cancel()
            for pass_line in to_cancel_passes:
                pass_line.message_post(body=_("Refunded on order %s") % line.order_id.session_id.name)

    def _find_passes_to_negate(self):
        self.ensure_one()
        return self.order_id.generated_pass_ids.filtered(
            lambda r: (
                r.product_id.detailed_type == "pass" and
                r.state in ["valid", "draft"]
            )
        )

    def _cancel_negated_event_pass(self):
        """
        Cancel the event pass linked to the order line if the order is negated.
        """
        to_process = self.filtered(
            lambda line: line.product_id.detailed_type == "pass" and int(line.qty) < 0 and not line.refunded_orderline_id
        )
        for line in to_process:
            to_cancel_qty = max(0, -int(line.qty))
            passes = line._find_passes_to_negate()
            passes = passes[-to_cancel_qty:]
            passes.action_cancel()
