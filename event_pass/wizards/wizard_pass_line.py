# Copyright 2024 Moka Tourisme (https://www.mokatourisme.fr).
# Author: Romain Duciel <romain@mokatourisme.fr>
# Author: Horvat Damien <ultrarushgame@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
import base64
from datetime import datetime, timedelta, date

from uuid import uuid4
from datetime import date


class WizardPassLine(models.TransientModel):
    _name = "wizard.pass.line"
    _description = "Wizard for ease pass creation"

    display_name = fields.Char(string="Name of the pass", required=True, readonly=False)
    number_pass = fields.Integer(string="Number of pass", required=True, default=1)
    validity_date = fields.Date(string="Validity Date", required=True, compute='compute_validity_date', store=True,
                                readonly=False,
                                help="The date when the pass becomes valid. If not set, it will default to today.")
    pass_type_id = fields.Many2one(comodel_name="event.pass.type", string="Pass Type")
    expiration_date = fields.Date(string="Expiration Date", required=False, compute='compute_expiration_date',
                                  store=True, readonly=False,
                                  help="The date when the pass expires. If not set, it will default to 1 year after the validity date.")
    fixed_number_allowed_event = fields.Boolean(string="Fixed Allowed attendance", default=False,
                                                compute='_compute_fixed_number_allowed_event', readonly=False,
                                                store=True)
    fixed_number_visitors_allowed = fields.Boolean(
        string="Fixed number visitors",
        help="Fixed number of visitors allowed per event(s)/session(s)",
        default=False,
        compute='_compute_fixed_number_visitors_allowed', readonly=False, store=True,
    )

    number_allowed_event = fields.Integer(string="Allowed attendance", default=1,
                                          compute='_compute_number_allowed_event', readonly=False, store=True)
    number_visitors = fields.Integer(string="Allowed attendees", default=1, compute='_compute_number_visitors',
                                     readonly=False, store=True)
    event_stage_ids = fields.Many2many("event.stage", string="Stage", compute='_compute_event_stage_ids', store=True,
                                       readonly=False)
    event_ids = fields.Many2many("event.event", string="Event", compute="_compute_event_ids", store=True,
                                 readonly=False)
    event_type_ids = fields.Many2many("event.type", string="Event Type", compute="_compute_event_type_ids", store=True,
                                      readonly=False)
    session_ids = fields.Many2many("event.session", string="Session", compute="_compute_session_ids", store=True,
                                   readonly=False,
                                   help="Sessions where the pass can be used. If empty, the pass can be used for all sessions of the event.")
    unauthorized_session_ids = fields.Many2many("event.session", "event_pass_line_wizard_unauthorized_session_rel",
                                                string="Unauthorized Session",
                                                compute='_compute_unauthorized_session_ids', store=True, readonly=False,
                                                help="Sessions where the pass cannot be used. If empty, the pass can be used for all sessions of the event.")
    category_ids = fields.Many2many("event.tag", string="Category", compute="_compute_category_ids", store=True,
                                    readonly=False, help="Categories of the pass. If empty, the pass can be used")
    partner_id = fields.Many2one(comodel_name="res.partner",
                                 default=lambda self: self.env.context.get("default_partner_id", False),
                                 ondelete="cascade", required=False, readonly=False)
    gifted_by_id = fields.Many2one(comodel_name="res.partner", string="Gifted by", ondelete="restrict", required=False,
                                   readonly=False)

    use_validity_dates = fields.Boolean(
        string="Use Validity Dates", help="Use Validity Dates",
    )

    @api.depends('pass_type_id')
    def compute_validity_date(self):
        for record in self:
            if record.pass_type_id.validity_option == 'fixed':
                record.validity_date = record.pass_type_id.validity_date
            else:
                record.validity_date = date.today()

    @api.depends('pass_type_id')
    def compute_expiration_date(self):
        for record in self:
            if record.pass_type_id.validity_option == 'fixed':
                record.expiration_date = record.pass_type_id.expiration_date
            else:
                record.expiration_date = record.validity_date + timedelta(days=record.pass_type_id.validity_period)

    @api.model
    def default_get(self, fields):
        res = super(WizardPassLine, self).default_get(fields)
        if 'validity_date' in fields:
            res['validity_date'] = date.today()
        return res

    @api.depends('pass_type_id')
    def _compute_event_stage_ids(self):
        for record in self:
            record.event_stage_ids = record.pass_type_id.event_stage_ids

    @api.depends('pass_type_id')
    def _compute_event_ids(self):
        for record in self:
            record.event_ids = record.pass_type_id.event_ids

    @api.depends('pass_type_id')
    def _compute_event_type_ids(self):
        for record in self:
            record.event_type_ids = record.pass_type_id.event_type_ids

    @api.depends('pass_type_id')
    def _compute_session_ids(self):
        for record in self:
            record.session_ids = record.pass_type_id.session_ids

    @api.depends('pass_type_id')
    def _compute_unauthorized_session_ids(self):
        for record in self:
            record.unauthorized_session_ids = record.pass_type_id.unauthorized_session_ids

    @api.depends('pass_type_id')
    def _compute_category_ids(self):
        for record in self:
            record.category_ids = record.pass_type_id.category_ids

    @api.depends('pass_type_id')
    def _compute_fixed_number_allowed_event(self):
        for record in self:
            record.fixed_number_allowed_event = record.pass_type_id.fixed_number_allowed_event

    @api.depends('pass_type_id')
    def _compute_number_allowed_event(self):
        for record in self:
            record.number_allowed_event = record.pass_type_id.number_allowed_event

    @api.depends('pass_type_id')
    def _compute_fixed_number_visitors_allowed(self):
        for record in self:
            record.fixed_number_visitors_allowed = record.pass_type_id.fixed_number_visitors_allowed

    @api.depends('pass_type_id')
    def _compute_number_visitors(self):
        for record in self:
            record.number_visitors = record.pass_type_id.number_visitors

    def _generate_code_line_pass(self):
        return '051' + str(uuid4().int)[:10]

    def _create_pass_lines(self):
        self.ensure_one()
        pass_lines_vals = []
        for i in range(self.number_pass):
            pass_lines_vals.append({
                "display_name": self.display_name,
                "pass_type_id": self.pass_type_id.id,
                "validity_date": self.validity_date,
                "expiration_date": self.expiration_date if self.expiration_date else False,
                "fixed_number_allowed_event": self.fixed_number_allowed_event,
                "fixed_number_visitors_allowed": self.fixed_number_visitors_allowed,
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
