# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import base64


class PosOrder(models.Model):
    _inherit = "pos.order"

    generated_pass_ids = fields.One2many(
        "event.pass.line", "pos_order_line_id", string="Bought Pass", readonly=True,
    )

    pass_count = fields.Integer(
        compute="_compute_pass_count",
        help="The number of pass related to this order",
        groups="point_of_sale.group_pos_user",
    )

    def _compute_pass_count(self):
        for record in self:
            record.pass_count = self.env['event.pass.line'].search_count([('id', 'in', record.lines.generated_pass_ids.ids)])

    def action_view_pass(self):
        action = self.env['ir.actions.act_window']._for_xml_id('event_pass.action_pass')
        action["domain"] = [("id", "in", self.lines.generated_pass_ids.ids)]
        return action

    def action_pass_partner_view(self):
        action = self.env["ir.actions.actions"]._for_xml_id("event_pass.action_pass")
        action['context'] = {}
        action['domain'] = ['|', ('partner_id', '=', self.id), ('gifted_by_id', '=', self.id)]
        return action

    @api.model
    def create_from_ui(self, orders, draft=False):
        order_ids = super(PosOrder, self).create_from_ui(orders, draft)
        for order in self.sudo().browse([o["id"] for o in order_ids]):
            for line in order.lines:
                # Change condition and check if the object is a pass to create pass
                if line.product_id.detailed_type == "pass":
                # End of condition
                    if not line.pass_id:
                        new_pass = line._create_pass()

        return order_ids
