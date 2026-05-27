from odoo import fields, models


class PassLine(models.Model):
    _inherit = "event.pass.line"

    partner_phone = fields.Char(
        related="partner_id.phone",
        string="Téléphone",
        store=True,
    )
