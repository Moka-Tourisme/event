# Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
# @author Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class EventRegistration(models.Model):
    _inherit = "event.registration"

    def _get_website_registration_allowed_fields(self):
        return super()._get_website_registration_allowed_fields() | {"session_id"}
