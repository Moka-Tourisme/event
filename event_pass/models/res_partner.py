# Copyright 2024 Moka Tourisme (https://www.mokatourisme.fr).
# Author: Romain Duciel <romain@mokatourisme.fr>
# Author: Horvat Damien <ultrarushgame@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ResPartnerEventPass(models.Model):
    _inherit = 'res.partner'

    pass_line_ids = fields.One2many('event.pass.line', 'partner_id')

    pass_count = fields.Integer('# Passes', compute='_compute_pass_count', groups='event.group_event_registration_desk',
                                help='Number of passes the partner has.')

    def _compute_pass_count(self):
        self.pass_count = 0
        for partner in self:
            partner.pass_count = self.env['event.pass.line'].search_count(['|', ('partner_id', '=', partner.id), ('gifted_by_id', '=', partner.id)])

    def action_pass_partner_view(self):
        action = self.env["ir.actions.actions"]._for_xml_id("event_pass.action_pass")
        action['context'] = {}
        action['domain'] = ['|', ('partner_id', '=', self.id), ('gifted_by_id', '=', self.id)]
        return action