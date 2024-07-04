from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    website_published = fields.Boolean('Published on Website', default=False)
    