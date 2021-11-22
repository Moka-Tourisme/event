# Copyright 2021 Moka Tourisme (https://www.mokatourisme.fr).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import NotFound

from odoo.http import Controller, content_disposition, request, route


class EventSessionController(Controller):
    @route(
        ["""/event/session/<model("event.session"):session>/ics"""],
        type="http",
        auth="public",
    )
    def event_session_ics_file(self, session, **kwargs):
        """Similar to core :meth:`~event_ics_file` for event.event"""
        files = session._get_ics_file()
        if session.id not in files:
            return NotFound()
        content = files[session.id]
        return request.make_response(
            content,
            [
                ("Content-Type", "application/octet-stream"),
                ("Content-Length", len(content)),
                ("Content-Disposition", content_disposition("%s.ics" % session.name)),
            ],
        )
