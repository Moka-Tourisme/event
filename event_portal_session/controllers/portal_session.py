from collections import OrderedDict
from operator import itemgetter
from markupsafe import Markup

from odoo import conf, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

from odoo.osv.expression import OR, AND


class EventCustomerPortalSession(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'event_session_count' in counters:
            event_session_count = request.env['event.session'].search_count(self._get_sessions_domain()) \
                if request.env['event.session'].check_access_rights('read', raise_exception=False) else 0
            values['event_session_count'] = event_session_count
        return values

    def _get_sessions_domain(self):
        user = request.env.user
        is_portal_user = user.has_group('base.group_portal')
        is_admin_user = user.has_group('event.group_event_manager')
        if is_portal_user:
            domain = [
                ('organizer_id', '=', user.partner_id.id),
                ('is_finished', '!=', True)
            ]
        elif is_admin_user :
            domain = [
                ('is_finished', '!=', True)
            ]
        else : 
            domain = [
            '|',
            '|',
            ('organizer_id', '=', user.partner_id.id),
            ('message_follower_ids.partner_id', '=', user.partner_id.id),
            ('is_finished', '!=', True) 
        ]
            
        return domain


    # ------------------------------------------------------------
    # My Sessions
    # ------------------------------------------------------------
    def _session_get_page_view_values(self, session, access_token, page=1, date_begin=None, date_end=None, sortby=None,
                                      search=None, search_in='content', groupby=None, **kwargs):
        values = self._prepare_portal_layout_values()

        # default sort by value
        if not sortby:
            sortby = 'date'

        domain = [('id', '=', session.id)]
        print('session recommandée : ', session.id)
        # Pagination et filtre par date
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        Session = request.env['event.session']
        if access_token:
            Session = Session.sudo()
        else:
            domain = AND([domain, request.env['ir.rule']._compute_domain(Session._name, 'read')])
            Session = Session.sudo()

        session_count = Session.search_count(domain)
        url = "/my/event/sessions/session/%s" % session.id
        pager = portal_pager(
            url=url,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'groupby': groupby,
                      'search_in': search_in, 'search': search},
            total=session_count,
            page=page,
            step=self._items_per_page
        )

        sessions = Session.search(domain, limit=self._items_per_page, offset=pager['offset'])

        # Stockage dans l'historique
        request.session['my_event_sessions_history'] = sessions.ids[:100]

        # Gestion des boutons précédent et suivant
        history = request.session.get('my_event_sessions_history', [])
        if session.id in history:
            current_index = history.index(session.id)
            prev_record = history[current_index - 1] if current_index > 0 else False
            next_record = history[current_index + 1] if current_index < len(history) - 1 else False
        else:
            prev_record = next_record = False

        values.update(
            date=date_begin,
            date_end=date_end,
            default_url=url,
            pager=pager,
            search_in=search_in,
            search=search,
            sortby=sortby,
            groupby=groupby,
            session=session,
            prev_record=prev_record,
            next_record=next_record
        )
        return self._get_page_view_values(session, access_token, values, 'my_event_sessions_history', False, **kwargs)

    @http.route(['/my/event/sessions/<int:event_id>', '/my/event/sessions/page/<int:page>'], type='http', auth="user",
                website=True)
    def portal_my_event_sessions(self, page=1, event_id=None, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        user = request.env.user.partner_id.id
        Session = request.env['event.session']
        domain = [('event_id', '=', event_id)]

        session_count = Session.search_count(domain)
        pager = portal_pager(
            url="/my/event/sessions",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=session_count,
            page=page,
            step=self._items_per_page
        )

        sessions = Session.search(domain, limit=self._items_per_page, offset=pager['offset'])

        # Mise à jour de l'historique des sessions visualisées
        request.session['my_event_sessions_history'] = sessions.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'sessions': sessions,
            'page_name': 'event_sessions',
            'default_url': '/my/event/sessions',
            'pager': pager,
            'sortby': sortby,
            'user': user
        })
        return request.render("event_portal_session.portal_my_sessions", values)

    @http.route(['/my/event/sessions/session/<int:session_id>'], type='http', auth="public", website=True)
    def portal_my_session(self, session_id=None, access_token=None, page=1, date_begin=None, date_end=None, sortby=None,
                          search=None, search_in='content', groupby=None, **kw):
        try:
            session_sudo = self._document_check_access('event.session', session_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        session_sudo = session_sudo if access_token else session_sudo.with_user(request.env.user)
        values = self._session_get_page_view_values(session_sudo, access_token, page, date_begin, date_end, sortby,
                                                    search, search_in, groupby, **kw)
        return request.render("event_portal_session.portal_my_session", values)
