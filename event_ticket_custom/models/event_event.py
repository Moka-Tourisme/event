# Copyright 2024 Moka Tourisme (https://www.mokatourisme.fr).
# @author Horvat Damien <ultrarushgame@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import is_html_empty


class EventEvent(models.Model):
    _inherit = "event.event"


    ticket_bottom_left = fields.Html(
        string="bottom_left",
        help="This information will be printed on your tickets on back left position. Use a custom image to set it to full screen",
    )

    bottom_left_full_screen_image = fields.Boolean(
        string="Full Screen Image",
        help="This will set the bottom left image to full screen",
        default=False,
    )

    ticket_upper_left = fields.Html(
        string="upper_left",
        help="This information will be printed on your tickets on top left position",
        compute="_compute_ticket_extra_info",
        store=True,
        readonly=False,
        translate=True,
    )

    upper_left_full_screen_image = fields.Boolean(
        string="Full Screen Image",
        help="This will set the upper left image to full screen",
        default=False,
    )

    ticket_bottom_right = fields.Html(
        string="bottom_right",
        help="This information will be printed on your tickets on back right position",
        compute="_compute_ticket_fold_info",
        store=True,
        readonly=False,
        translate=True,
    )

    bottom_right_full_screen_image = fields.Boolean(
        string="Full Screen Image",
        help="This will set the bottom right image to full screen",
        default=False,
    )

    background_color = fields.Char(
        string="Background Color",
        default="#FFFFFF",
    )

    outline_color = fields.Char(
        string="Outline Color",
        default="#F8F4E8",
    )

    content_color = fields.Char(
        string="Content Color",
        default="#000000",
    )

    title_color = fields.Char(
        string="Title Color",
        default="#000000",
    )

    base_logo = fields.Binary(
        string="Base Logo",
        help="Logo on the ticket",
    )

    logo_position = fields.Integer(
        string="Logo Position",
        default=70,
        help="-10 to 100. Corresponds to the top property in css",
    )

    logo_width = fields.Integer(
        string="Logo Width",
        default=130,
        help="Width of the logo in pixels from 0 to 160",
    )

    logo_height = fields.Integer(
        string="Logo Height",
        default=170,
        help="Height of the logo in pixels from 0 to 170",
    )





    @api.depends("event_type_id")
    def _compute_ticket_extra_info(self):
        for event in self:
            if is_html_empty(event.ticket_upper_left) and not is_html_empty(
                event.event_type_id.ticket_upper_left
            ):
                event.ticket_upper_left = event.event_type_id.ticket_upper_left

    @api.depends("event_type_id")
    def _compute_ticket_fold_info(self):
        for event in self:
            if is_html_empty(event.ticket_bottom_right) and not is_html_empty(
                event.event_type_id.ticket_bottom_right
            ):
                event.ticket_bottom_right = event.event_type_id.ticket_bottom_right