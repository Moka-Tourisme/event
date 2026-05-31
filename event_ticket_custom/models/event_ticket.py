# Copyright 2024 Moka Tourisme (https://www.mokatourisme.fr).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class EventEventTicket(models.Model):
    _inherit = 'event.event.ticket'

    def _get_ticket_multiline_description(self):
        # Use raw name instead of display_name to avoid [Company] suffix from name_get()
        return self.name + '\n' + self.event_id.display_name
