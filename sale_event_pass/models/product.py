from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _inherit = "product.product"

    pass_type_id = fields.Many2one(
        "event.pass.type",
        string="Modèle de Pass (variante)",
        help="Surcharge le modèle de pass défini sur le gabarit produit pour cette variante uniquement.",
    )

    def _get_pass_type(self):
        """Retourne le modèle de pass effectif : variante en priorité, sinon le gabarit."""
        self.ensure_one()
        return self.pass_type_id or self.product_tmpl_id.pass_type_id


class ProductTemplate(models.Model):
    _inherit = "product.template"

    detailed_type = fields.Selection(selection_add=[
        ('pass', 'Pass'),
    ], ondelete={'pass': 'set service'})

    pass_type_id = fields.Many2one(
        "event.pass.type",
        string="Pass Type",
    )

    location_id = fields.Many2one(
        "res.partner",
        store=True,
    )

    def _detailed_type_mapping(self):
        type_mapping = super()._detailed_type_mapping()
        type_mapping['pass'] = 'service'
        return type_mapping

    # When creating or updating a product with detailed_type = pass, we need to check that the pass_type_id is set
    @api.constrains('detailed_type', 'pass_type_id')
    def _check_pass_type_id(self):
        for product in self:
            if product.detailed_type == 'pass' and not product.pass_type_id:
                raise UserError(_('Pass type is required for pass products'))
