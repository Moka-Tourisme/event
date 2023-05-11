# Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http, fields
from odoo.http import request

from odoo.addons.website_event.controllers.main import WebsiteEventController


class WebsiteEventSessionController(WebsiteEventController):
    def _create_attendees_from_registration_post(self, event, registration_data):
        # OVERRIDE to add event_session_id into context.
        # We need this context key present so that the call to :meth:`_cart_update`
        # knows which event_session_id to use.
        if event.use_sessions:
            # We assume they all share the same session_id, as that's expected
            session_id = registration_data and registration_data[0]["session_id"]
            request.website = request.website.with_context(event_session_id=session_id)
        return super()._create_attendees_from_registration_post(
            event, registration_data
        )

    @http.route(type="json")
    def session_tickets(self, session):
        # OVERRIDE to add ticket price info
        res = super().session_tickets(session)
        pricelist = request.website.get_current_pricelist()
        currency = pricelist.currency_id
        ticket_ids = [t["id"] for t in res]
        tickets = request.env["event.event.ticket"].browse(ticket_ids)
        tickets = tickets.with_context(
            pricelist=pricelist.id,
            partner=request.env.user.partner_id,
        )
        MonetaryConverter = request.env["ir.qweb.field.monetary"]
        currency_opts = {"display_currency": currency}
        for ticket, data in zip(tickets, res):
            converted_ticket_price = request.website.company_id.currency_id._convert(
                ticket.price,
                currency,
                request.website.company_id,
                fields.Datetime.now()
            )
            converted_ticket_price_reduce = request.website.company_id.currency_id._convert(
                ticket.price_reduce,
                currency,
                request.website.company_id,
                fields.Datetime.now()
            )
            data.update(
                {
                    "price": converted_ticket_price,
                    "price_reduce": converted_ticket_price_reduce,
                    "currency": {
                        "name": currency.name,
                    },
                    "price_html": MonetaryConverter.value_to_html(
                        converted_ticket_price, currency_opts
                    ),
                    "price_reduce_html": MonetaryConverter.value_to_html(
                        converted_ticket_price_reduce, currency_opts
                    ),
                }
            )
        return res
