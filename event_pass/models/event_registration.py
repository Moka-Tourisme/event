# Copyright 2024 Moka Tourisme (https://www.mokatourisme.fr).
# Author: Romain Duciel <romain@mokatourisme.fr>
# Author: Horvat Damien <ultrarushgame@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    pass_line_id = fields.Many2one(
        "event.pass.line", string="Pass Line", ondelete="restrict"
    )
    pass_type_id = fields.Many2one(
        "event.pass.type", string="Pass Type", related="pass_line_id.pass_type_id", store=True
    )

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res.pass_line_id:
            events = self.env["event.event"].search(
                [("registration_ids.pass_line_id", "=", res.pass_line_id.id),
                 ("use_sessions", "=", False)]
            )
            sessions = self.env["event.session"].search(
                [("registration_ids.pass_line_id", "=", res.pass_line_id.id)]
            )
            res.pass_line_id.write({"counted_passage": len(events) + len(sessions)})
        if res.pass_line_id.fixed_number_allowed_event:
            res.pass_line_id.write({"remaining_passage": res.pass_line_id.remaining_passage - 1})
            if res.pass_line_id.remaining_passage <= 0:
                res.pass_line_id.write({'state': 'expired'})
        return res
