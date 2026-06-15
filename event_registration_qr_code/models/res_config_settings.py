# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    show_qr_code_text = fields.Boolean(
        string="Show QR Code Value on Tickets",
        config_parameter="event_registration_qr_code.show_qr_code_text",
        help="Display the QR code value as readable text below the QR code on "
        "printed tickets (badge and full page).",
    )
