from odoo import api, fields, models


class PassLine(models.Model):
    _inherit = "event.pass.line"

    pos_order_line_id = fields.Many2one(
        "pos.order.line",
        copy=False,
        readonly=True,
        help="Pos Order line where this pass has been bought.",
    )

    pos_order_id = fields.Many2one(
        "pos.order",
        string="Pos Order",
        related="pos_order_line_id.order_id",
        store=True,
        ondelete="cascade",
        copy=False,
    )

    pos_order_count = fields.Integer(
        compute="_compute_pos_order",
        help="The number of point of sales orders related to this pass",
        groups="point_of_sale.group_pos_user",
    )

    def _compute_pos_order(self):
        for record in self:
            record.pos_order_count = self.env['pos.order'].search_count([('lines.generated_pass_ids', 'in', record.id)])

    def action_view_pos_order(self):
        action = self.env['ir.actions.act_window']._for_xml_id('point_of_sale.action_pos_pos_form')
        action["domain"] = [("lines.generated_pass_ids", "in", self.id)]
        return action


class PassType(models.Model):
    _inherit = 'event.pass.type'

    pos_order_count = fields.Integer(
        compute="_compute_pos_order",
        help="The number of point of sales orders related to this pass",
        groups="point_of_sale.group_pos_user",
    )

    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        related='company_id.currency_id', readonly=True)

    pos_price_subtotal = fields.Monetary(
        string="POS Sales (Tax Excluded)",
        compute="_compute_pos_price_subtotal",
        currency_field='currency_id',
        groups="point_of_sale.group_pos_user",
    )

    def _compute_pos_order(self):
        for record in self:
            record.pos_order_count = self.env['pos.order'].search_count([('lines.product_id.pass_type_id', '=', record.id)])

    def action_view_pos_order(self):
        action = self.env['ir.actions.act_window']._for_xml_id('point_of_sale.action_pos_pos_form')
        action["domain"] = [("lines.product_id.pass_type_id", "=", self.id)]
        return action

    def _compute_pos_price_subtotal(self):
        for record in self:
            pos_order_lines = self.env['pos.order.line'].search([
                ('product_id.pass_type_id', '=', self.id),
                ('order_id.state', '!=', 'cancel'),
                ('price_subtotal', '!=', 0),
            ])
            pos_price_subtotals = pos_order_lines.mapped('price_subtotal')
            record.currency_id = self.env.company.currency_id
            record.pos_price_subtotal = record.currency_id._convert(
                sum(pos_price_subtotals), self.env.company.currency_id, self.env.company, fields.Date.today()
            )

    def action_view_pos_orders(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "point_of_sale.action_pos_pos_form"
        )
        action["domain"] = [
            ("state", "!=", "cancel"),
            ("lines.product_id.pass_type_id", "=", self.id),
        ]
        return action
