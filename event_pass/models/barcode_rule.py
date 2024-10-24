# Copyright 2024 Moka Tourisme (https://www.mokatourisme.fr).
# Author: Romain Duciel <romain@mokatourisme.fr>
# Author: Horvat Damien <ultrarushgame@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BarcodeRuleInherit(models.Model):
    _inherit = 'barcode.rule'

    type = fields.Selection(
        selection_add=[
            ('pass', 'Pass'),
        ],
        ondelete={'pass': 'set product'},
    )
