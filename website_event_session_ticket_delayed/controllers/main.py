# Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import pytz

from datetime import datetime
from datetime import timedelta
from pytz import timezone, UTC, utc

from odoo import _, fields, http

from odoo.addons.website_event_session.controllers.main import WebsiteEventController


class WebsiteEventSessionController(WebsiteEventController):

    @http.route(type="json")
    def session_tickets(self, session):
        """Returns the list of available tickets for the selected session"""
        tickets = super().session_tickets(session)

        for ticket in tickets:
            ticket['start_sell_delay'] = session.event_ticket_ids.filtered(lambda t: t.id == ticket["id"]).start_sell_delay
            ticket['end_sell_delay'] = session.event_ticket_ids.filtered(lambda t: t.id == ticket["id"]).end_sell_delay
            ticket['start_sell_delay_hours'] = int(ticket['start_sell_delay'])
            ticket['start_sell_delay_minutes'] = int((ticket['start_sell_delay'] - ticket['start_sell_delay_hours']) * 60)
            ticket['end_sell_delay_hours'] = int(ticket['end_sell_delay'])
            ticket['end_sell_delay_minutes'] = int((ticket['end_sell_delay'] - ticket['end_sell_delay_hours']) * 60)

        event_tz = timezone(session.date_tz) if session.date_tz else UTC

        filtered_tickets = [
            ticket
            for ticket in tickets
            if (
                       not ticket['start_sell_delay'] and not ticket['end_sell_delay']
               ) or (
                       ticket['start_sell_delay'] and utc.localize(datetime.now()).astimezone(event_tz).replace(tzinfo=None) >= (
                       utc.localize(session.date_begin).astimezone(event_tz).replace(tzinfo=None) - timedelta(hours=tickets[0]['start_sell_delay_hours'], minutes=tickets[0][
                   'start_sell_delay_minutes']))
               ) or (
                       ticket['end_sell_delay'] and utc.localize(datetime.now()).astimezone(event_tz).replace(tzinfo=None) <= (
                       utc.localize(session.date_begin).astimezone(event_tz).replace(tzinfo=None) - timedelta(hours=tickets[0]['end_sell_delay_hours'], minutes=tickets[0][
                   'end_sell_delay_minutes']))
               )
        ]
        return filtered_tickets
