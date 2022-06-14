# Copyright 2022 Moka Tourisme (https://www.mokatourisme.fr).
# @author Laffeach bryan <laffeach.bryan@hotmail.fr>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EventEvent(models.Model):
    _inherit = "event.event"

    phone_required = fields.Boolean("Phone is required ?")
