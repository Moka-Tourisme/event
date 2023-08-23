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
    """Event"""
    _inherit = 'event.session'

    @api.model
    def get_current_user_tickets(self, session_id):
        """Returns the tickets for the current user"""
        current_user = self.env.user
        registrations = self.env['event.registration'].search([
            ('session_id', '=', session_id),
            ('partner_id', '=', current_user.partner_id.id),
            ('state', 'in', ['open', 'done'])
        ])
        return registrations
