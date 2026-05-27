# Copyright 2024 Moka Tourisme (https://www.mokatourisme.fr).
# Author: Romain Duciel <romain@mokatourisme.fr>
# Author: Horvat Damien <ultrarushgame@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class WizardEventPass(models.TransientModel):
    _name = "wizard.event.pass"
    _description = "Wizard for ease pass creation"

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        default=lambda self: self.env.context["active_id"],
        ondelete="cascade",
        required=True,
        readonly=True,
    )