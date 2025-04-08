from odoo import api, fields, models
from odoo.tools import date_utils


class PosSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_product_product(self):
        params = super()._loader_params_product_product()
        params["search_params"]["fields"].append("detailed_type")
        params["search_params"]["fields"].append("location_id")
        params["search_params"]["fields"].append("pass_type_id")
        return params
