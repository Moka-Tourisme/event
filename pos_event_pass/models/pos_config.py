# Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
# @author Bryan Laffeach <laffeach.bryan@hotmail.fr>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class PointOfSaleConfig(models.Model):
    _inherit = "pos.config"

    iface_print_pass = fields.Boolean(
        "Print Pass QR Code on receipt",
    )

