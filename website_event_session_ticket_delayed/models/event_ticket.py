# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class EventEventTicket(models.Model):
    _inherit = "event.event.ticket"

    start_sell_delay = fields.Float(
        string="Start sell delay",
        help="Delay in days before the ticket can be bought from the start of the session",
        default=None,
    )

    end_sell_delay = fields.Float(
        string="End buy delay",
        help="Delay in days before the ticket can't be bought from the start of the session",
        default=None,
    )


class EventTemplateTicket(models.Model):
    _inherit = "event.type.ticket"

    start_sell_delay = fields.Float(
        string="Start sell delay",
        help="Delay in days before the ticket can be bought from the start of the session",
        default=None,
    )

    end_sell_delay = fields.Float(
        string="End buy delay",
        help="Delay in days before the ticket can't be bought from the start of the session",
        default=None,
    )

    @api.model
    def _get_event_ticket_fields_whitelist(self):
        """Add website specific field to copy from template to ticket"""
        return super(EventTemplateTicket, self)._get_event_ticket_fields_whitelist() + [
            "start_sell_delay",
            "end_sell_delay",
        ]
