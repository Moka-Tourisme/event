# Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import functools
import itertools
from datetime import datetime, timedelta

from odoo import _, fields, http
from odoo.exceptions import MissingError
from odoo.http import request

from odoo.addons.website_event.controllers.main import WebsiteEventController


class WebsiteEventSessionController(WebsiteEventController):
    @http.route(
        "/event/<model('event.event'):event>/session_dates",
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
        sitemap=False,
    )
    def session_dates(self, event, date_begin=None, date_end=None, **post):
        """Get session dates and availability

        Note: we add a +/- 1 day margin on date_begin and date_end
        to account for possible timezone differences. (FIXME)

        :param date_begin: If set, filter sessions starting from.
        :param date_end:   If set, filter sessions ending before.
        """
        domain = [("event_id", "=", event.id)]
        if date_begin:
            date_begin = fields.Date.from_string(date_begin)
            date_begin = date_begin - timedelta(days=1)
            domain.append(("date_begin", ">=", date_begin))
        if date_end:
            date_end = fields.Date.from_string(date_end)
            date_end = date_end + timedelta(days=1)
            domain.append(("date_end", "<=", date_end))
        # Get sessions.
        # The order is important for efficiency in groupby
        sessions = request.env["event.session"].search(domain, order="date_begin asc")
        # Group by day and compute seats availability
        res = {}
        by_day = itertools.groupby(sessions, lambda s: s.date_begin.date())
        for day, group in by_day:
            day_sessions = functools.reduce(lambda s1, s2: s1 | s2, group)
            day_key = fields.Date.to_string(day)
            res[day_key] = {
                "sessions_count": len(day_sessions),
                "seats_limited": not any(not s.seats_limited for s in day_sessions),
                "seats_available": sum(
                    s.seats_available for s in day_sessions if s.seats_limited
                ),
            }
        return res

    @http.route(
        "/event/<model('event.event'):event>/sessions_for_date",
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
        sitemap=False,
    )
    def sessions_for_date(self, event, date):
        """Get sessions for a given date"""
        date = fields.Date.from_string(date)
        # TODO: date_begin and date_end used in domain should account for event tz
        # it's possible we miss some records otherwise
        domain = [
            ("event_id", "=", event.id),
            ("date_begin", ">=", datetime.combine(date, datetime.min.time())),
            ("date_begin", "<=", datetime.combine(date, datetime.max.time())),
        ]
        sessions = request.env["event.session"].search(domain)
        res = []
        for session in sessions:
            date_begin_tz = fields.Datetime.context_timestamp(
                session._set_tz_context(), session.date_begin
            )
            res.append(
                {
                    "id": session.id,
                    "display_name": date_begin_tz.strftime("%H:%M"),
                    "seats_limited": session.seats_limited,
                    "seats_available": session.seats_available,
                }
            )
        return res

    @http.route(
        "/event/session/<model('event.session'):session>/tickets",
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
        sitemap=False,
    )
    def session_tickets(self, session):
        """Returns the list of available tickets for the selected session"""
        return [
            {
                "id": ticket.id,
                "name": ticket.name,
                "description": ticket.description,
                "seats_limited": ticket.seats_limited,
                "seats_available": ticket.seats_available,
                "seats_max": ticket.seats_max,
            }
            for ticket in session.event_ticket_ids
        ]

    @http.route()
    def registration_new(self, event, **post):
        # COMPLETE OVERRIDE to handle events with sessions
        if not event.use_sessions:
            return super().registration_new(event, **post)

        session_id = int(post.pop("event_session_id", None))
        session = request.env["event.session"].browse(session_id)
        if session.event_id != event:
            raise MissingError(_("The session does not exist."))

        tickets = self._process_tickets_form(event, post)
        availability_check = True
        if session.seats_limited:
            ordered_seats = 0
            for ticket in tickets:
                ordered_seats += ticket["quantity"]
            if session.seats_available < ordered_seats:
                availability_check = False
        if not tickets:
            return False
        default_first_attendee = {}
        if not request.env.user._is_public():
            default_first_attendee = {
                "name": request.env.user.name,
                "email": request.env.user.email,
                "phone": request.env.user.mobile or request.env.user.phone,
            }
        else:
            visitor = request.env["website.visitor"]._get_visitor_from_request()
            if visitor.email:
                default_first_attendee = {
                    "name": visitor.name,
                    "email": visitor.email,
                    "phone": visitor.mobile,
                }
        return request.env["ir.ui.view"]._render_template(
            "website_event.registration_attendee_details",
            {
                "tickets": tickets,
                "event": event,
                "session": session,
                "availability_check": availability_check,
                "default_first_attendee": default_first_attendee,
            },
        )

    @http.route()
    def event_registration_success(self, event, registration_ids):
        # OVERRIDE to include the session in the rendering context
        #
        # It's difficult to get the session id without changing the method signature,
        # as it doesn't accept kwargs, and we get here from a redirect from
        # :meth:`registration_confirm`.
        #
        # However, the registration ids are passed as a query string parameter and we
        # can get the session from there.
        res = super().event_registration_success(event, registration_ids)
        if event.use_sessions:
            res.qcontext["session"] = fields.first(res.qcontext["attendees"].session_id)
        return res
