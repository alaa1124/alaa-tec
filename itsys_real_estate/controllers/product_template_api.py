from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import json

class CustomWebsiteSale(WebsiteSale):

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True, **kw):
        order = request.website.sale_get_order(force_create=1)
        if order.state != 'draft':
            request.website.sale_reset()
            if kw.get('force_create'):
                order = request.website.sale_get_order(force_create=1)
            else:
                return {}

        existing_line = order.order_line.filtered(lambda l: l.product_id.id == int(product_id))
        if existing_line:
            return {'error': 'This product is already in the cart'}

        return super().cart_update_json(
            product_id=product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            display=display,
            **kw
        )

    @http.route(['/shop/cart/updates'], type='http', auth="public", methods=['POST'], website=True)
    def custom_cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        sale_order = request.website.sale_get_order(force_create=True)

        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)

        if sale_order.order_line.filtered(lambda l: l.product_id.id == int(product_id)):
            return request.redirect("/shop/cart")

        product_custom_attribute_values = json.loads(kw.get('product_custom_attribute_values', '{}'))
        no_variant_attribute_values = json.loads(kw.get('no_variant_attribute_values', '{}'))

        sale_order._cart_update(
            product_id=int(product_id),
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values
        )

        if kw.get('express'):
            return request.redirect("/shop/checkout?express=1")

        return request.redirect("/shop/cart")
