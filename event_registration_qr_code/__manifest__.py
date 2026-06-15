# Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Event Registration QR Code",
    "summary": "Automatically generate unique QR Codes for each registration",
    "version": "16.0.1.1.0",
    "author": "Moka Tourisme, Odoo Community Association (OCA)",
    "maintainers": ["ivantodorovich"],
    "website": "https://github.com/OCA/event",
    "license": "AGPL-3",
    "category": "Marketing",
    "depends": ["event"],
    "data": [
        "views/event_registration.xml",
        "views/res_config_settings.xml",
        "reports/report_templates.xml",
    ],
}
