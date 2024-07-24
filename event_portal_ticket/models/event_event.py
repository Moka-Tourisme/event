# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

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
    def get_current_user_tickets_count(self, event_id):
        current_user = self.env.user.partner_id.id
        registrations = self.env['event.registration'].search([
            ('event_id', '=', event_id),
            ('partner_id', '=', current_user),
            ('state', 'in', ['open', 'done'])
        ])
        return len(registrations)
    
    @api.model
    def get_attendees(self, event_id):
        registrations = self.env['event.registration'].search([
            ('event_id', '=', event_id),
            ('state', 'in', ['open', 'done'])
        ])
        return len(registrations)