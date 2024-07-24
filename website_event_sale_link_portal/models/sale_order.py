import logging
import random
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, models, fields, _
from odoo.http import request
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    @api.model
    def has_event_ticket(self, order_id):
        order = self.browse(order_id)
        if order:
            for line in order.order_line:
                if line.event_ticket_id:
                    return True
        return False

