# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    detailed_type = fields.Selection(selection_add=[
        ('pass', 'Pass'),
    ], ondelete={'pass': 'set service'})

    pass_type_id = fields.Many2one(
        "event.pass.type",
        string="Pass Type",
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
