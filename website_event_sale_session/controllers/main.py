# Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

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
