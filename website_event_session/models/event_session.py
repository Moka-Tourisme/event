# Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import werkzeug
from pytz import utc

from odoo import api, fields, models

from odoo.addons.website_event.models.event_event import GOOGLE_CALENDAR_URL


class EventSession(models.Model):
    _inherit = "event.session"

    is_ongoing = fields.Boolean(
        compute="_compute_time_data",
        help="Whether the session has begun",
    )
    is_done = fields.Boolean(
        compute="_compute_time_data",
        help="Whether the session is finished",
    )
    start_today = fields.Boolean(
        compute="_compute_time_data",
        help="Whether the session is going to start today if still not ongoing",
    )
    start_remaining = fields.Integer(
        string="Remaining before start",
        compute="_compute_time_data",
        help="Remaining time before event starts (minutes)",
    )

    @api.depends("date_begin", "date_end")
    def _compute_time_data(self):
        """Similar to :meth:`event_event._compute_time_data` but for sessions"""
        now_utc = utc.localize(fields.Datetime.now().replace(microsecond=0))
        for rec in self:
            date_begin_utc = utc.localize(rec.date_begin, is_dst=False)
            date_end_utc = utc.localize(rec.date_end, is_dst=False)
            rec.is_ongoing = date_begin_utc <= now_utc <= date_end_utc
            rec.is_done = now_utc > date_end_utc
            rec.start_today = date_begin_utc.date() == now_utc.date()
            if date_begin_utc >= now_utc:
                td = date_begin_utc - now_utc
                rec.start_remaining = int(td.total_seconds() / 60)
            else:
                rec.start_remaining = 0

    def _get_event_resource_urls(self):
        """Similar to :meth:`event_event._get_event_resource_urls` but for sessions"""
        url_date_start = self.date_begin.strftime("%Y%m%dT%H%M%SZ")
        url_date_stop = self.date_end.strftime("%Y%m%dT%H%M%SZ")
        params = {
            "action": "TEMPLATE",
            "text": self.name,
            "dates": url_date_start + "/" + url_date_stop,
            "details": self.name,
        }
        if self.address_id:
            params.update(
                location=self.sudo().address_id.contact_address.replace("\n", " ")
            )
        encoded_params = werkzeug.urls.url_encode(params)
        google_url = GOOGLE_CALENDAR_URL + encoded_params
        iCal_url = "/event/%d/ics?%s" % (self.id, encoded_params)
        return {"google_url": google_url, "iCal_url": iCal_url}
