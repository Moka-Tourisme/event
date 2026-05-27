# Copyright 2024 Moka Tourisme (https://www.mokatourisme.fr).
# @author Horvat Damien <ultrarushgame@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EventType(models.Model):
    _inherit = "event.type"

    ticket_upper_left = fields.Html(
        string="Ticket Extra Information",
        help="This information will be printed on your tickets.",
        translate=True,
    )
    ticket_bottom_right = fields.Html(
        string="Ticket Fold Information",
        help="This information will be printed on your tickets.",
        translate=True,
    )