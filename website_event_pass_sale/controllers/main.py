# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class WebsiteEventPassSale(http.Controller):

    @http.route(['/event/passes'], type='http', auth="public", website=True)
    def event_passes(self, **kwargs):
        products = request.env['product.template'].search([('website_published', '=', True), ('detailed_type', '=', 'pass')])
        return request.render('website_event_pass_sale.event_passes_page', {
            'products': products,
        })

    @http.route(['/event/pass/<model("product.template"):product>'], type='http', auth="public", website=True)
    def event_pass(self, product, **kwargs):
        return request.render('website_event_pass_sale.event_pass_page', {
            'product': product,
        })
