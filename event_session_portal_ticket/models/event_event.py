import logging
import pytz

from odoo import _, api, Command, fields, models
from odoo.addons.base.models.res_partner import _tz_get
from odoo.tools import format_datetime, is_html_empty
from odoo.exceptions import ValidationError
from odoo.tools.translate import html_translate

_logger = logging.getLogger(__name__)


class EventEventInherit(models.Model):
    _inherit = 'event.event'

    @api.model
    def get_current_user_sessions(self, event_id):
        current_user = self.env.user
        sessions = self.env['event.session'].search([
            ('event_id', '=', event_id),
            ('registration_ids.partner_id', '=', current_user.partner_id.id),
            ('registration_ids.state', 'in', ['open', 'done']),
            ('stage_id.id', '!=', 5),
        ])

        return sessions
    
    def get_sessions_count(self, event_id):
        current_user = self.env.user
        registrations = self.env['event.registration'].search([
            ('event_id', '=', event_id),
            ('partner_id', '=', current_user.partner_id.id),
            ('state', '!=', 'cancel'),
            ('state', 'in', ['open', 'done'])
        ])
        
        session_ids = registrations.mapped('session_id.id')
        session_count = len(set(session_ids))
        
        return session_count
    
    def get_sessions_registrations(self, sessions):
        registrations = self.env['event.registration'].search([
            ('session_id', 'in', sessions.ids),
            ('state', '!=', 'cancel'),
            ('state', 'in', ['open', 'done'])
        ])
        return registrations

    
    @api.model
    def get_participants_count(self, session_id):
        session = self.env['event.session'].browse(session_id)
        return len(session.registration_ids.filtered(lambda r: r.state in ['open', 'done']))