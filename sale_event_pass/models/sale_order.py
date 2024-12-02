import datetime

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    pass_count = fields.Integer(
        compute="_compute_pass_count",
        help="The number of pass related to this order",
    )

    def _compute_pass_count(self):
        for record in self:
            record.pass_count = self.env['event.pass.line'].search_count(
                [('id', 'in', record.order_line.generated_pass_ids.ids)])

    def action_view_pass(self):
        action = self.env['ir.actions.act_window']._for_xml_id('event_pass.action_pass')
        action["domain"] = [("id", "in", self.order_line.generated_pass_ids.ids)]
        return action

    @api.constrains('state')
    def _constrains_pass_state(self):
        for record in self.filtered(lambda so: so.state == 'sale'):
            for pass_order_line in record.order_line.filtered(lambda ol: ol.product_id.detailed_type == 'pass'):
                pass_order_line._create_pass()
            record.sudo()._send_pass_mail()

    def _send_pass_mail(self):
        template = self.env.ref('sale_event_pass.mail_template_pass', raise_if_not_found=False)
        if template and self.pass_count:
            for pass_line in self.order_line.mapped("generated_pass_ids"):
                template.send_mail(pass_line.id, force_send=True)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    generated_pass_ids = fields.One2many('event.pass.line', "buy_line_id", string="Bought Pass")
    pass_id = fields.Many2one('event.pass.line', help="Pass created", copy=False)

    def _create_pass(self):
        if self.order_id.state == 'sale':
            return self.env['event.pass.line'].create(
                [self._build_pass() for _ in range(int(self.product_uom_qty))]
            )

    def _build_pass(self):
        val_validity_date = self.product_id.pass_type_id.validity_date or fields.Date.today()
        return {
            "display_name": self.product_id.pass_type_id.display_name,
            "product_id": self.product_id.id,
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
            "buy_line_id": self.id,
            "pass_type_id": self.product_id.pass_type_id.id,
        }
