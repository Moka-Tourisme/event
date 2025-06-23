# Copyright 2024 Moka Tourisme (https://www.mokatourisme.fr).
# Author: Romain Duciel <romain@mokatourisme.fr>
# Author: Horvat Damien <ultrarushgame@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import logging
import psycopg2
import imghdr

from odoo import api, fields, models, registry, SUPERUSER_ID, _
from datetime import datetime, timedelta, date
from uuid import uuid4, UUID
from odoo.addons.base.models.ir_qweb_fields import nl2br
from odoo.modules import get_resource_path
from odoo.tools import html2plaintext, is_html_empty
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PassType(models.Model):
    _name = 'event.pass.type'
    _description = 'Pass Template'
    _rec_name = 'display_name'

    display_name = fields.Char(
        store=True,
    )

    name = fields.Char(
        string="Pass Name",
    )

    validity_option = fields.Selection([
        ('fixed', 'Fixed Date Range'),
        ('variable', 'Variable in Days')
    ], string="Validity Option", default='fixed')

    validity_date = fields.Date(
        string="Validity Date", help="Validity date of the pass if not set the validity date is the date of sale",
    )

    use_validity_dates = fields.Boolean(
        string="Use Validity Dates", help="Use Validity Dates",
    )

    validity_period = fields.Integer(
        string="Validity Period",
        help="Validity period of the pass in days, if not set the validity period is unlimited",
    )

    fixed_expiration_date = fields.Boolean(
        string="Fixed Expiration Date",
        help="Fixed expiration date of the pass",
        default=False,
    )

    expiration_date = fields.Date(
        string="Expiration Date",
        help="Expiration date of the pass if not set the expiration date is the validity date + validity period",
    )

    fixed_number_allowed_event = fields.Boolean(
        string="Fixed Allowed attendance",
        help="Fixed number of attendance allowed per pass/invitation",
        default=False,
    )

    pass_ids = fields.One2many(
        "event.pass.line",
        "pass_type_id",
        string="Pass",
        help="Pass line",
    )

    pass_ids_count = fields.Integer(
        string="Pass Count",
        compute='_compute_pass_ids_count',
        help="Number of pass line",
    )

    number_allowed_event = fields.Integer(
        string="Allowed attendance",
        help="Number of attendance allowed per pass/invitation",
        default=1,
    )

    number_visitors = fields.Integer(
        string="Allowed attendees",
        help="Number of attendees allowed per event(s)/session(s)",
        default=1,
    )

    event_stage_ids = fields.Many2many(
        "event.stage",
        string="Stage",
    )

    event_ids = fields.Many2many(
        "event.event",
        string="Event",
    )

    event_type_ids = fields.Many2many(
        "event.type",
        string="Event Type",
    )

    session_ids = fields.Many2many(
        "event.session",
        string="Session",
    )

    unauthorized_session_ids = fields.Many2many(
        "event.session",
        "event_pass_type_unauthorized_session_rel",
        string="Unauthorized Session",
    )

    category_ids = fields.Many2many(
        "event.tag",
        string="Category",
    )

    company_id = fields.Many2one(
        'res.company', string='Company', change_default=True,
        default=lambda self: self.env.company,
        required=False)

    base_logo = fields.Html(
        string="Base Logo",
        help="Please insert image by using /image",
    )

    base_logo_filename = fields.Char(
        string="Base Logo Filename",
    )

    title_color = fields.Char(
        string="Title Color",
        default="#E1B35B",
    )

    title_text = fields.Char(
        string="Title Text",
        help="Title text of the pass, leave empty to use the display name of the pass",
    )

    content_color = fields.Char(
        string="Content Color",
        default="#FFFFFF",
    )

    outline_color = fields.Char(
        string="Outline Color",
        default="#E1B35B",
    )

    background_color = fields.Char(
        string="Background Color",
        default="#2B2726",
    )

    bottom_right_text = fields.Html(
        string="Bottom right text",
        help="Text zone",
    )

    upper_left_text = fields.Html(
        string="Upper left text",
        help="Text zone",
    )

    bottom_left_text = fields.Html(
        string="Bottom left text",
        help="Text zone",
    )

    pdf_file = fields.Html(
        string="PDF View",
        help="PDF view of the pass",
        sanitize=False,
        sanitize_tags=False,
        sanitize_attributes=False,
        sanitize_style=False,
        sanitize_form=False,
        strip_style=False,
        strip_classes=False
    )

    fixed_number_visitors_allowed = fields.Boolean(
        string="Fixed number visitors",
        help="Fixed number of visitors allowed per event(s)/session(s)",
        default=False,
    )

    @api.model
    def default_get(self, fields_list):
        res = super(PassType, self).default_get(fields_list)
        res['display_name'] = self.env.context.get('default_name', '')
        res['validity_date'] = date.today()
        return res

    @api.constrains('expiration_date')
    def _check_expiration_date(self):
        for record in self:
            if record.expiration_date and record.validity_date and record.expiration_date < record.validity_date:
                raise ValidationError(_("Expiration date must be after validity date."))

    @api.depends('pass_ids')
    def _compute_pass_ids_count(self):
        for record in self:
            record.pass_ids_count = len(record.pass_ids)


class PassLine(models.Model):
    _name = "event.pass.line"
    _description = "Event Pass Line"
    _rec_name = "name"
    _inherit = ["mail.thread", "mail.activity.mixin", "portal.mixin"]

    name = fields.Char(
        compute='_compute_name',
    )

    def _compute_access_url(self):
        super()._compute_access_url()
        for pass_line in self:
            pass_line.access_url = '/my/pass/%s' % (pass_line.id)

    def _get_report_base_filename(self):
        return 'Pass_' + str(self.qr_code)

    display_name = fields.Char(
        required=True,
        string="Pass Name",
        help="Pass name",
    )

    pass_type_id = fields.Many2one(
        "event.pass.type",
        string="Pass Type",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("valid", "Valid"),
            ("expired", "Expired"),
            ("cancelled", "Cancelled"),
        ],
        string="State",
        default="draft",
        compute="_compute_state",
        store=True,
        required=True,
        readonly=True,
        copy=False,
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    validity_date = fields.Date(
        string="Validity Date", required=True,
        compute='_compute_validity_date', store=True, readonly=False, copy=True
    )

    expiration_date = fields.Date(
        string="Expiration Date",
        required=False,
        compute='_compute_expiration_date', store=True, readonly=False, copy=True
    )

    use_validity_dates = fields.Boolean(
        string="Use Validity Dates", help="Use Validity Dates",
    )

    fixed_number_allowed_event = fields.Boolean(
        string="Fixed Allowed attendance",
        help="Fixed number of attendance allowed per pass/invitation",
        default=False,
        compute='_compute_fixed_number_allowed_event', store=True, readonly=False, copy=True
    )

    fixed_number_visitors_allowed = fields.Boolean(
        string="Fixed number visitors",
        help="Fixed number of visitors allowed per event(s)/session(s)",
        default=False,
        compute='_compute_fixed_number_visitors_allowed', store=True, readonly=False, copy=True
    )

    number_allowed_event = fields.Integer(
        string="Allowed attendance",
        help="Number of attendance allowed per pass/invitation",
        compute='_compute_number_allowed_event', store=True, readonly=False, copy=True
    )

    number_visitors = fields.Integer(
        string="Allowed attendees",
        help="Number of attendees allowed per event(s)/session(s)",
        compute='_compute_number_allowed_visitors', store=True, readonly=False, copy=True
    )

    internal_notes = fields.Text(
        string="Note",
        help="Note of the pass",
    )

    counted_passage = fields.Integer(
        string="Counted passage",
        help="Number of passage counted",
        readonly=True,
    )

    remaining_passage = fields.Integer(
        string="Remaining passage",
        help="Number of passage remaining",
        readonly=True,
    )

    event_stage_ids = fields.Many2many(
        "event.stage",
        string="Stage",
        compute="_compute_event_stage_ids", readonly=False, store=True, copy=True
    )

    event_ids = fields.Many2many(
        "event.event",
        string="Event",
        compute='_compute_event_ids', readonly=False, store=True, copy=True
    )

    event_type_ids = fields.Many2many(
        "event.type",
        string="Event Type",
        compute="_compute_event_type_ids", readonly=False, store=True, copy=True
    )

    session_ids = fields.Many2many(
        "event.session",
        string="Session",
        compute='_compute_session_ids', readonly=False, store=True, copy=True
    )

    unauthorized_session_ids = fields.Many2many(
        "event.session",
        "event_pass_line_unauthorized_session_rel",
        string="Unauthorized Session",
        compute='_compute_unauthorized_session_ids', readonly=False, store=True, copy=True
    )

    category_ids = fields.Many2many(
        "event.tag",
        string="Category",
        compute='_compute_category_ids', readonly=False, store=True, copy=True
    )

    company_id = fields.Many2one(
        'res.company', string='Company', change_default=True,
        default=lambda self: self.env.company,
        required=False)

    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        related='company_id.currency_id', readonly=True)

    qr_code = fields.Char(default=lambda x: x._generate_code_line_pass(), required=True, readonly=True, copy=False)

    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
        default=lambda self: self.env.context.get("active_id", False),
        help="Customer of the pass, that can set a beneficiary if needed",
    )

    beneficiary = fields.Char(
        string="Beneficiary",
        help="Beneficiary of the pass if not set the beneficiary is the customer",
    )

    beneficiary_mail = fields.Char(
        string="Beneficiary Mail",
        help="Beneficiary mail of the pass",
    )

    gifted_by_id = fields.Many2one(
        "res.partner",
        "Gifted by",
        help="Gifted by",
    )

    event_count = fields.Integer(
        '# Events', compute='_compute_event_count', groups='event.group_event_registration_desk',
        help='Number of events the pass_line is used.')

    def _compute_event_count(self):
        for record in self:
            record.event_count = self.env['event.event'].search_count(
                [('registration_ids.pass_line_id', '=', record.id)])

    def action_event_view(self):
        action = self.env["ir.actions.actions"]._for_xml_id("event.action_event_view")
        action['context'] = {}
        action['domain'] = [('registration_ids.pass_line_id', '=', self.id)]
        return action

    @api.model
    def default_get(self, fields):
        res = super(PassLine, self).default_get(fields)
        if 'validity_date' in fields:
            res['validity_date'] = date.today()
        return res

    @api.model
    def create(self, vals):
        records = super(PassLine, self).create(vals)
        for rec in records:
            self._check_barcode_exist(rec)
        return records

    def _check_barcode_exist(self, rec):
        if not rec.partner_id.barcode:
            rec.partner_id.update({
                'barcode': self._generate_code(),
            })

    @api.depends('state', 'validity_date', 'expiration_date')
    def _compute_state(self):
        for record in self:
            if record.state == 'draft':
                if record.validity_date and record.validity_date <= fields.Date.today():
                    record.state = 'valid'
                elif record.expiration_date and record.expiration_date <= fields.Date.today():
                    record.state = 'expired'
                else:
                    record.state = 'draft'
            elif record.state == 'valid':
                if record.expiration_date and record.expiration_date <= fields.Date.today():
                    record.state = 'expired'
            elif record.state == 'expired':
                if not (record.validity_date and record.validity_date <= fields.Date.today()):
                    record.state = 'draft'

    @api.model
    def _generate_code(self):
        return '042' + str(uuid4().int)[:10]

    @api.model
    def _generate_code_line_pass(self):
        return '051' + str(uuid4().int)[:10]

    def _update_previous_pass_code(self):
        pass_lines = self.env['event.pass.line'].search([('qr_code', 'not ilike', '051%')])
        for pass_line in pass_lines:
            pass_line.qr_code = self._generate_code_line_pass()

    def action_send_multiple_by_mail(self, type):
        records = self
        if any(record.gifted_by_id for record in records):
            for record in records:
                if record.gifted_by_id != records[0].gifted_by_id:
                    raise UserError(_('Please set the same "Gifted by" for all records.'))

        pdf_data = self._get_pdf_data(records, type)
        pdf_file = self._create_attachement(records, pdf_data, type.capitalize())
        if type == 'pass':
            template = self.env.ref('event_pass.pass_mail_template').id
        else:
            template = self.env.ref('event_pass.invitation_mail_template').id

        context = {
            'default_model': self._name,
            'default_res_id': records[0].id,
            'default_use_template': True,
            'default_template_id': template,
            'default_attachment_ids': pdf_file.ids,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
        }

        if records[0].gifted_by_id:
            context.update({
                'default_partner_ids': [records[0].gifted_by_id.id],
            })

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': context,
        }

    def action_send_pass_by_mail(self):
        record = self
        pdf_data = self._get_pdf_data(record, "pass")
        pdf_file = self._create_attachement(record, pdf_data, "Pass")
        context = {
            'default_model': self._name,
            'default_res_id': record.id,
            'default_use_template': True,
            'default_template_id': self.env.ref('event_pass.pass_mail_template').id,
            'default_attachment_ids': pdf_file.ids,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
        }
        if record.partner_id:
            context.update({
                'default_partner_ids': [record.partner_id.id],
            })
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': context,
        }

    def _create_attachement(self, records, pdf_data, type):
        attachment_name = type + '_tickets.pdf'
        attachment_vals = {
            'name': attachment_name,
            'datas': base64.b64encode(pdf_data),
            'type': 'binary',
            'res_model': self._name,
            'res_id': records[0].id,
            'mimetype': 'application/pdf',
        }
        return self.env['ir.attachment'].create(attachment_vals)

    def _get_pdf_data(self, records, type):
        if type == "pass":
            report = 'event_pass.pass_report'
        else:
            report = 'event_pass.invitation_report'
        pdf_data, _ = self.env['ir.actions.report']._render_qweb_pdf(report, res_ids=records.ids)
        return pdf_data

    def action_confirm(self):
        if self.filtered(lambda pass_line: pass_line.state not in ['draft']):
            raise UserError(_("Only draft pass can be confirmed."))
        return self.write({'state': 'valid'})

    def action_cancel(self):
        if self.filtered(lambda pass_line: pass_line.state not in ['valid', 'draft', 'expired']):
            raise UserError(_("Only valid, draft or expired pass can be cancelled."))
        return self.write({'state': 'cancelled'})

    def action_draft(self):
        if self.filtered(lambda pass_line: pass_line.state != 'cancelled'):
            raise UserError(_("Only cancelled pass can be draft."))
        return self.write({'state': 'draft'})

    def action_open_pass_line_wizard(self):
        action = self.env["ir.actions.actions"]._for_xml_id("event_pass.act_wizard_event_pass_line")
        return action

    def _cron_check_validity(self):
        pass_lines = self.env['event.pass.line'].search([
            '|',
            '&',
            ('validity_date', '<=', fields.Date.today()),
            ('state', '=', 'draft'),
            ('expiration_date', '=', False)
        ])
        pass_lines.write({'state': 'valid'})

        pass_lines = self.env['event.pass.line'].search([
            ('expiration_date', '<=', fields.Date.today()),
            ('state', '=', 'valid')
        ])
        pass_lines.write({'state': 'expired'})

    @api.depends('display_name', 'qr_code')
    def _compute_name(self):
        for record in self:
            record.name = record.display_name + ' - ' + record.qr_code

    @api.depends('pass_type_id')
    def _compute_event_stage_ids(self):
        for record in self:
            record.event_stage_ids = record.pass_type_id.event_stage_ids

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
    def _compute_event_ids(self):
        for record in self:
            record.event_ids = record.pass_type_id.event_ids

    @api.depends('pass_type_id')
    def _compute_fixed_number_allowed_event(self):
        for record in self:
            record.fixed_number_allowed_event = record.pass_type_id.fixed_number_allowed_event

    @api.depends('pass_type_id')
    def _compute_fixed_number_visitors_allowed(self):
        for record in self:
            record.fixed_number_visitors_allowed = record.pass_type_id.fixed_number_visitors_allowed

    @api.depends('pass_type_id')
    def _compute_number_allowed_event(self):
        for record in self:
            record.number_allowed_event = record.pass_type_id.number_allowed_event

    @api.depends('pass_type_id')
    def _compute_number_allowed_visitors(self):
        for record in self:
            record.number_visitors = record.pass_type_id.number_visitors

    @api.depends('pass_type_id')
    def _compute_validity_date(self):
        for record in self:
            if record.pass_type_id.validity_option == 'fixed':
                record.validity_date = record.pass_type_id.validity_date
            else:
                record.validity_date = date.today()

    @api.depends('pass_type_id')
    def _compute_expiration_date(self):
        for record in self:
            if record.pass_type_id.validity_option == 'fixed':
                if record.pass_type_id.fixed_expiration_date:
                    record.expiration_date = record.pass_type_id.expiration_date
                else:
                    record.expiration_date = record.validity_date + timedelta(days=record.pass_type_id.validity_period)
