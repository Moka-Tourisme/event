# Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Website Event Session",
    "summary": "Website Event Session",
    "version": "15.0.1.0.0",
    "author": "Moka Tourisme, Odoo Community Association (OCA)",
    "maintainers": ["ivantodorovich"],
    "website": "https://github.com/OCA/event",
    "license": "AGPL-3",
    "category": "Marketing",
    "depends": ["website_event", "event_session"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/event_templates_list.xml",
        "views/event_templates_page_registration.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "website_event_session/static/src/js/website_event_session_booking.js",
            "website_event_session/static/src/js/website_event_ticket_details.js",
        ]
    },
    "auto_install": True,
}
