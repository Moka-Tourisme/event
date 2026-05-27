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
        pass_type = self.product_id._get_pass_type()
        if pass_type.validity_option == 'fixed':
            validity_date = pass_type.validity_date or fields.Date.today()
            expiration_date = pass_type.expiration_date
        else:
            validity_date = fields.Date.today()
            expiration_date = validity_date + datetime.timedelta(days=pass_type.validity_period) if pass_type.validity_period else False
        return {
            "display_name": pass_type.display_name,
            # "product_id": self.product_id.id,
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
            "buy_line_id": self.id,
            "pass_type_id": pass_type.id,
        }
