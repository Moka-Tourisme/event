# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict

from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.osv.expression import AND

from ...event_portal_ticket.controllers.portal import EventTicketCustomerPortal, portal_pager


class EventSessionTicketCustomerPortal(EventTicketCustomerPortal):
    def _prepare_portal_layout_values(self):
        """Values for /my/* templates rendering.

        Does not include the record counts.
        """
        # get customer sales rep
        sales_user = False
        partner = request.env.user.partner_id
        if partner.user_id and not partner.user_id._is_public():
            sales_user = partner.user_id

        return {
            'sales_user': sales_user,
            'page_name': 'home',
        }

    # ------------------------------------------------------------
    # My Session
    # ------------------------------------------------------------
    def _session_get_page_view_values(self, session, access_token, page=1, date_begin=None, date_end=None, sortby=None,
                                      search=None, search_in='content', groupby=None, **kwargs):
        # TODO: refactor this because most of this code is duplicated from portal_my_events_tickets method
        values = self._prepare_portal_layout_values()

        # default sort by value
        if not sortby:
            sortby = 'date'

        # default filter by value
        domain = [('id', '=', session.id)]

        # default group by value
        if not groupby:
            groupby = 'session'

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        Session = request.env['event.session']
        if access_token:
            Session = Session.sudo()
        elif not request.env.user._is_public():
            domain = AND([domain, request.env['ir.rule']._compute_domain(Session._name, 'read')])
            Session = Session.sudo()

        # event count
        session_count = Session.search_count(domain)
        # pager
        url = "/my/tickets/event/session/%s" % session.id
        pager = portal_pager(
            url=url,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'groupby': groupby,
                      'search_in': search_in, 'search': search},
            total=session_count,
            page=page,
            step=self._items_per_page
        )

        events = Session.search(domain, limit=self._items_per_page, offset=pager['offset'])
        # request.session['my_event_events_history'] = events.ids[:100]

        values.update(
            date=date_begin,
            date_end=date_end,
            page_name='sessions',
            default_url=url,
            pager=pager,
            search_in=search_in,
            search=search,
            sortby=sortby,
            groupby=groupby,
            session=session,
            registrations=session.registration_ids.filtered(lambda
                                                                r: r.partner_id.id == request.env.user.partner_id.id and r.state != 'cancel' and r.state != 'draft'),
            registration_ids=','.join(map(str, session.registration_ids.filtered(lambda
                                                                                     r: r.partner_id.id == request.env.user.partner_id.id and r.state != 'cancel' and r.state != 'draft').ids)),
        )
        return self._get_page_view_values(session, access_token, values, 'my_events_history', False, **kwargs)

    def _get_sessions_domain(self, event_id, user):
        return [
            ('event_id', '=', event_id),
            ('registration_ids.partner_id', '=', user)
        ]

    @http.route(['/my/tickets/event/sessions/<int:event_id>'], type='http', auth="public", website=True)
    def portal_my_event_sessions(self, event_id=None, access_token=None, page=1, date_begin=None, date_end=None,
                                 sortby=None, search=None, search_in='content', groupby=None, filterby=None, **kw):
        values = self._prepare_portal_layout_values()
        Session = request.env['event.session']
        user = request.env.user.partner_id.id
        domain = []

        domain += self._get_sessions_domain(event_id, user)

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
            'upcoming': {'label': _('Upcoming'), 'domain': [('stage_id', 'in', [1, 2, 3])]},
        }

        if not filterby:
            filterby = 'upcoming'
        domain += searchbar_filters[filterby]['domain']

        # sessions count
        session_count = Session.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/tickets/event/sessions/%s" % event_id,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'groupby': groupby,
                      'search_in': search_in, 'search': search, 'filterby': filterby},
            total=session_count,
            page=page,
            step=self._items_per_page
        )

        sessions = Session.search(domain, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_event_sessions_history'] = sessions.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'page_name': 'sessions',
            'default_url': '/my/tickets/event/sessions/%s' % event_id,
            'pager': pager,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'sessions': sessions,
            'filterby': filterby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
        })
        return request.render("event_session_portal_ticket.portal_my_event_sessions", values)

    @http.route(['/my/tickets/event/session/<int:session_id>'], type='http', auth="public", website=True)
    def portal_my_event_session(self, session_id=None, access_token=None, **kw):
        session = request.env['event.session'].browse(session_id)
        values = self._session_get_page_view_values(session, access_token, **kw)
        return request.render("event_session_portal_ticket.portal_my_event_session_tickets", values)
