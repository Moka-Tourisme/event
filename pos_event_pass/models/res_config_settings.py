# Copyright 2022 Moka (https://www.moka.cloud).
# @author Bryan Laffeach <laffeach.bryan@hotmail.fr>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    iface_print_pass = fields.Boolean(
        "Print Pass QR Code on receipt",
    )

