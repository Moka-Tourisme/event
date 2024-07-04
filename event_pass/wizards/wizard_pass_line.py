# Copyright 2024 Moka Tourisme (https://www.mokatourisme.fr).
# Author: Romain Duciel <romain@mokatourisme.fr>
# Author: Horvat Damien <ultrarushgame@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
import base64
from uuid import uuid4

class WizardPassLine(models.TransientModel):
    _name = "wizard.pass.line"
    _description = "Wizard for ease pass creation"

    display_name = fields.Char(string="Name of the pass", required=True, readonly=False)
    number_pass = fields.Integer(string="Number of pass", required=True, default=1)
    validity_date = fields.Date(string="Validity Date", required=True)
    pass_type_id = fields.Many2one(comodel_name="event.pass.type", string="Pass Type")
    expiration_date = fields.Date(string="Expiration Date")
    fixed_number_allowed_event = fields.Boolean(string="Fixed Allowed attendance", default=False)
    number_allowed_event = fields.Integer(string="Allowed attendance", default=1)
    number_visitors = fields.Integer(string="Allowed attendees", default=1)
    event_stage_ids = fields.Many2many("event.stage", string="Stage")
    event_ids = fields.Many2many("event.event", string="Event")
    event_type_ids = fields.Many2many("event.type", string="Event Type")
    session_ids = fields.Many2many("event.session", string="Session")
    unauthorized_session_ids = fields.Many2many("event.session", "event_pass_line_wizard_unauthorized_session_rel", string="Unauthorized Session")
    category_ids = fields.Many2many("event.tag", string="Category")
    partner_id = fields.Many2one(comodel_name="res.partner", default=lambda self: self.env.context.get("default_partner_id", False), ondelete="cascade", required=False, readonly=False)
    gifted_by_id = fields.Many2one(comodel_name="res.partner", string="Gifted by", ondelete="restrict", required=False, readonly=False)

    def _generate_code_line_pass(self):
        # Generate a unique QR code for each pass line
        return str(uuid4())

    def _create_pass_lines(self):
        self.ensure_one()
        pass_lines_vals = []
        for i in range(self.number_pass):
            pass_lines_vals.append({
                "display_name": self.display_name,
                "pass_type_id": self.pass_type_id.id,
                "validity_date": self.validity_date,
                "expiration_date": self.expiration_date,
                "fixed_number_allowed_event": self.fixed_number_allowed_event,
                "number_allowed_event": self.number_allowed_event,
                "number_visitors": self.number_visitors,
                "event_stage_ids": [(6, 0, self.event_stage_ids.ids)],
                "event_ids": [(6, 0, self.event_ids.ids)],
                "event_type_ids": [(6, 0, self.event_type_ids.ids)],
                "session_ids": [(6, 0, self.session_ids.ids)],
                "unauthorized_session_ids": [(6, 0, self.unauthorized_session_ids.ids)],
                "category_ids": [(6, 0, self.category_ids.ids)],
                "partner_id": self.partner_id.id,
                "gifted_by_id": self.gifted_by_id.id,
                "qr_code": self._generate_code_line_pass(),
            })
        return self.env["event.pass.line"].create(pass_lines_vals)

    def action_create_pass_lines(self):
        self.ensure_one()
        pass_lines = self._create_pass_lines()
        action = self.env.ref("event_pass.action_pass").read()[0]
        action['context'] = {}
        action['domain'] = [('id', 'in', pass_lines.ids)]
        return action

    def action_create_pass_lines_and_send(self):
        self.ensure_one()
        pass_lines = self._create_pass_lines()
        return pass_lines.action_send_multiple_by_mail("pass")
