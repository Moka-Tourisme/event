# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, registry, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError


class PassLine(models.Model):
    _inherit = "event.pass.line"

    buy_line_id = fields.Many2one("sale.order.line", copy=False, readonly=True,
                                  help="Sale Order line where this gift card has been bought.")

    sale_order_count = fields.Integer(compute='_compute_sale_order_count',
                                      string='The number of sales orders related to this pass',
                                      groups="base.group_user")
    
    commercial_team = fields.Many2one('crm.team', string='Commercial Team', compute='_compute_commercial_team', store=True)

    total_excluding_taxes = fields.Float(string='Total (taxes excl.)', compute='_compute_total_excluding_taxes', store=True)

    total_including_taxes = fields.Float(string='Total (taxes incl.)', compute='_compute_total_including_taxes',
                                         store=True)
    
    @api.depends('buy_line_id')
    def _compute_total_including_taxes(self):
        for record in self:
            if record.buy_line_id.price_total:
                record.total_including_taxes = record.buy_line_id.price_total

    @api.depends('buy_line_id')
    def _compute_total_excluding_taxes(self):
        for record in self:
            if record.buy_line_id:
                record.total_excluding_taxes = record.buy_line_id.price_subtotal

    @api.depends("buy_line_id")
    def _compute_commercial_team(self):
        for record in self:
            if record.buy_line_id.order_id.team_id:
                record.commercial_team = record.buy_line_id.order_id.team_id

    def _compute_sale_order_count(self):
        for record in self:
            record.sale_order_count = self.env['sale.order'].search_count(
                [('order_line.generated_pass_ids', 'in', record.id)])

    def action_view_sale_order(self):
        action = self.env['ir.actions.act_window']._for_xml_id('sale.act_res_partner_2_sale_order')
        action["domain"] = [("order_line.generated_pass_ids", "in", self.id)]
        return action


class PassType(models.Model):
    _inherit = 'event.pass.type'
    _description = 'Pass Template'
    _rec_name = 'display_name'
    # _order = 'sequence, id'

    display_name = fields.Char(
        string="Name of the pass",
        required=True,
    )

    validity_date = fields.Date(
        string="Validity Date", help="Validity date of the pass if not set the validity date is the date of sale",
    )

    validity_period = fields.Integer(
        string="Validity Period",
        help="Validity period of the pass in days, if not set the validity period is unlimited",
    )

    fixed_expiration_date = fields.Boolean(
        string="Fixed Expiration Date",
        help="Fixed expiration date of the pass",
        default=False,
    )

    expiration_date = fields.Date(
        string="Expiration Date",
        help="Expiration date of the pass if not set the expiration date is the validity date + validity period",
    )

    fixed_number_allowed_event = fields.Boolean(
        string="Fixed Allowed attendance",
        help="Fixed number of attendance allowed per pass/invitation",
        default=False,
    )

    number_allowed_event = fields.Integer(
        string="Allowed attendance",
        help="Number of attendance allowed per pass/invitation",
        default=1,
    )

    number_visitors = fields.Integer(
        string="Allowed attendees",
        help="Number of attendees allowed per event(s)/session(s)",
        default=1,
    )

    event_stage_ids = fields.Many2many(
        "event.stage",
        string="Stage",
    )

    event_ids = fields.Many2many(
        "event.event",
        string="Event",
    )

    event_type_ids = fields.Many2many(
        "event.type",
        string="Event Type",
    )

    session_ids = fields.Many2many(
        "event.session",
        string="Session",
    )

    unauthorized_session_ids = fields.Many2many(
        "event.session",
        "event_pass_type_unauthorized_session_rel",
        string="Unauthorized Session",
    )

    category_ids = fields.Many2many(
        "event.tag",
        string="Category",
    )

    product_count = fields.Integer(
        string="Product Count",
        compute="_compute_product_count",
    )

    sale_order_count = fields.Integer(
        string="Sale Order Count",
        compute="_compute_sale_order_count",
    )

    company_id = fields.Many2one(
        'res.company', string='Company', change_default=True,
        default=lambda self: self.env.company,
        required=False)

    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        related='company_id.currency_id', readonly=True)

    sale_price_subtotal = fields.Monetary(
        string="Sale Price Subtotal",
        compute="_compute_sale_price_subtotal",
        currency_field='currency_id',
    )

    def default_get(self, fields_list):
        res = super(PassType, self).default_get(fields_list)
        res['display_name'] = self.env.context.get('default_name', '')
        return res

    def _compute_currency_id(self):
        for record in self:
            record.currency_id = self.env.company.currency_id

    def _compute_product_count(self):
        for record in self:
            record.product_count = self.env['product.template'].search_count([('pass_type_id', '=', record.id)])

    def _compute_sale_order_count(self):
        for record in self:
            record.sale_order_count = self.env['sale.order'].search_count(
                [('order_line.product_id.pass_type_id', '=', record.id)])

    def _compute_sale_price_subtotal(self):
        for record in self:
            sale_order_lines = self.env['sale.order.line'].search([
                ('product_id.pass_type_id', '=', self.id),
                ('order_id.state', '!=', 'cancel'),
                ('price_subtotal', '!=', 0),
            ])
            sale_price_subtotals = sale_order_lines.mapped('price_subtotal')
            record.currency_id = self.env.company.currency_id
            record.sale_price_subtotal = record.currency_id._convert(
                sum(sale_price_subtotals), self.env.company.currency_id, self.env.company, fields.Date.today()
            )

    @api.constrains('expiration_date')
    def _check_expiration_date(self):
        # If expiration_date is before validity_date raise an error
        for record in self:
            if record.expiration_date and record.validity_date and record.expiration_date < record.validity_date:
                raise ValidationError(_("Expiration date must be after validity date."))

    def action_product_view(self):
        action = self.env["ir.actions.actions"]._for_xml_id("product.product_template_action_all")
        action['context'] = {}
        action['domain'] = [('pass_type_id', '=', self.id)]
        return action

    def action_view_sale_order(self):
        action = self.env['ir.actions.act_window']._for_xml_id('sale.act_res_partner_2_sale_order')
        action["domain"] = [("order_line.product_id.pass_type_id", "=", self.id)]
        return action

    def action_view_linked_orders(self):
        """ Redirects to the orders linked to the current events """
        sale_order_action = self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        sale_order_action.update({
            'domain': [('state', '!=', 'cancel'), ('order_line.product_id.pass_type_id', 'in', self.ids)],
            'context': {'create': 0},
        })
        return sale_order_action
