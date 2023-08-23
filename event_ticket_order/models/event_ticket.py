from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class EventTemplateTicketInherit(models.Model):
    _inherit = 'event.type.ticket'
    _order = "sequence ASC, id DESC"

    sequence = fields.Integer(string='Sequence', default=10)
