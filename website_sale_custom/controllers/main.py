# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import logging
from datetime import datetime

from psycopg2.errors import LockNotAvailable
from werkzeug.exceptions import Forbidden, NotFound
from werkzeug.urls import url_decode, url_encode, url_parse

from odoo import fields, http, SUPERUSER_ID, tools, _
from odoo.exceptions import AccessError, MissingError, UserError, ValidationError
from odoo.tools import SQL, lazy, str2bool
from odoo.http import request, content_disposition
from odoo.addons.website_sale.controllers.main import WebsiteSale, WebsiteSaleForm


_logger = logging.getLogger(__name__)


class WebsiteSaleFormCustom(WebsiteSaleForm):

    @http.route()
    def website_form_saleorder(self, **kwargs):

        res = super().website_form_saleorder(**kwargs)

        model_record = request.env.ref('sale.model_sale_order')
        # reservation_model_record = request.env.ref('itsys_real_estate.model_ownership_contract')

        try:
            data = self.extract_data(model_record, kwargs)
        except ValidationError as e:
            return json.dumps({'error_fields': e.args[0]})

        order = request.website.sale_get_order()
        if not order:
            return json.dumps({'error': "No order found; please add a product to your cart."})

        order.send_attachment()

        order.order_line.write({'active': False})

        order.cart_quantity = 0

        return res


class WebsiteSaleCustom(WebsiteSale):

    @http.route('/website/download/form/<int:company_id>/form_file', type='http', auth="public", website=True)
    def download_product_form(self, company_id, **kw):

        company_id = request.env['res.company'].sudo().browse(company_id)


        if company_id and company_id.form_file:
            filename = company_id.form_file_name or 'form.pdf'  # Provide a default filename
            return request.make_response(
                company_id.form_file,
                headers=[
                    ('Content-Type', 'application/octet-stream'),
                    ('Content-Disposition', content_disposition(filename))
                ]
            )
        else:
            return request.not_found()

    @http.route('/website/download/form/form_file', type='http', auth="public", website=True)
    def download_product_form2(self, **kw):

        product_template_id = request.env['product.template']

        order = request.website.sale_get_order()
        products = order.order_line.product_template_id

        if products:
            product_template_id = products[0]

        if product_template_id and product_template_id.form_file:
            filename = product_template_id.form_file_name or 'form.pdf'  # Provide a default filename
            return request.make_response(
                product_template_id.form_file,
                headers=[
                    ('Content-Type', 'application/octet-stream'),
                    ('Content-Disposition', content_disposition(filename))
                ]
            )
        else:
            return request.not_found()

    # /shop/checkout
    # @http.route()
    # def checkout(self, **post):
    #     order_sudo = request.website.sale_get_order()
    #     request.session['sale_last_order_id'] = order_sudo.id
    #     redirection = self.checkout_redirection(order_sudo)
    #     if order_sudo.partner_id:
    #         return request.redirect(f'/shop/address?mode=billing&partner_id={order_sudo.partner_id.id}')
    #
    #     if redirection:
    #         return redirection
    #
    #     if order_sudo._is_public_order():
    #         return request.redirect('/shop/address')
    #
    #     redirection = self.checkout_check_address(order_sudo)
    #     if redirection:
    #         return redirection
    #
    #     if post.get('express'):
    #         return request.redirect('/shop/confirm_order')
    #
    #     values = self.checkout_values(order_sudo, **post)
    #
    #     # Avoid useless rendering if called in ajax
    #     if post.get('xhr'):
    #         return 'ok'
    #     return request.render("website_sale.checkout", values)
    #
    # # /shop/address
    # @http.route()
    # def address(self, **kw):
    #     Partner = request.env['res.partner'].with_context(show_address=1).sudo()
    #     order = request.website.sale_get_order()
    #
    #     redirection = self.checkout_redirection(order)
    #     if redirection:
    #         return redirection
    #
    #     can_edit_vat = False
    #     values, errors = {}, {}
    #
    #     partner_id = int(kw.get('partner_id', -1))
    #     if order._is_public_order():
    #         mode = ('new', 'billing')
    #         can_edit_vat = True
    #     else:  # IF ORDER LINKED TO A PARTNER
    #         if partner_id > 0:
    #             if partner_id == order.partner_id.id:
    #                 # If we modify the main customer of the SO ->
    #                 # 'billing' bc billing requirements are higher than shipping ones
    #                 can_edit_vat = order.partner_id.can_edit_vat()
    #                 mode = ('edit', 'billing')
    #             else:
    #                 address_mode = kw.get('mode')
    #                 if not address_mode:
    #                     address_mode = 'shipping'
    #                     if partner_id == order.partner_invoice_id.id:
    #                         address_mode = 'billing'
    #
    #                 # Make sure the address exists and belongs to the customer of the SO
    #                 partner_sudo = Partner.browse(partner_id).exists()
    #                 partners_sudo = Partner.search(
    #                     [('id', 'child_of', order.partner_id.commercial_partner_id.ids)]
    #                 )
    #                 mode = ('edit', address_mode)
    #                 if address_mode == 'billing':
    #                     billing_partners = partners_sudo.filtered(lambda p: p.type != 'delivery')
    #                     if partner_sudo not in billing_partners:
    #                         raise Forbidden()
    #                 else:
    #                     shipping_partners = partners_sudo.filtered(lambda p: p.type != 'invoice')
    #                     if partner_sudo not in shipping_partners:
    #                         raise Forbidden()
    #
    #                 can_edit_vat = partner_sudo.can_edit_vat()
    #
    #             if mode and partner_id != -1:
    #                 values = Partner.browse(partner_id)
    #         elif partner_id == -1:
    #             mode = ('new', kw.get('mode') or 'shipping')
    #         else:  # no mode - refresh without post?
    #             return request.redirect('/shop/checkout')
    #
    #     # IF POSTED
    #     if 'submitted' in kw and request.httprequest.method == "POST":
    #         pre_values = self.values_preprocess(kw)
    #         errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
    #         post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)
    #
    #         if errors:
    #             errors['error_message'] = error_msg
    #             values = kw
    #         else:
    #             update_mode, address_mode = mode
    #             partner_id = self._checkout_form_save(mode, post, kw)
    #             # We need to validate _checkout_form_save return, because when partner_id not in shippings
    #             # it returns Forbidden() instead the partner_id
    #             if isinstance(partner_id, Forbidden):
    #                 return partner_id
    #
    #             fpos_before = order.fiscal_position_id
    #             update_values = {}
    #             if update_mode == 'new':  # New address
    #                 if order._is_public_order():
    #                     update_values['partner_id'] = partner_id
    #
    #                 if address_mode == 'billing':
    #                     update_values['partner_invoice_id'] = partner_id
    #                     if kw.get('use_same'):
    #                         update_values['partner_shipping_id'] = partner_id
    #                     elif (
    #                             order._is_public_order()
    #                             and not kw.get('callback')
    #                             and not order.only_services
    #                     ):
    #                         # Now that the billing is set, if shipping is necessary
    #                         # request the customer to fill the shipping address
    #                         kw['callback'] = '/contactus-thank-you'
    #                 elif address_mode == 'shipping':
    #                     update_values['partner_shipping_id'] = partner_id
    #             elif update_mode == 'edit':  # Updating an existing address
    #                 if order.partner_id.id == partner_id:
    #                     # Editing the main partner of the SO --> also trigger a partner update to
    #                     # recompute fpos & any partner-related fields
    #                     update_values['partner_id'] = partner_id
    #
    #                 if address_mode == 'billing':
    #                     update_values['partner_invoice_id'] = partner_id
    #                     if not kw.get('callback') and not order.only_services:
    #                         kw['callback'] = '/contactus-thank-you'
    #                 elif address_mode == 'shipping':
    #                     update_values['partner_shipping_id'] = partner_id
    #
    #             order.write(update_values)
    #
    #             if order.fiscal_position_id != fpos_before:
    #                 # Recompute taxes on fpos change
    #                 # TODO recompute all prices too to correctly manage price_include taxes ?
    #                 order._recompute_taxes()
    #
    #             if 'partner_id' in update_values:
    #                 # Force recomputation of pricelist on main customer address update
    #                 request.website.sale_get_order(update_pricelist=True)
    #
    #             # TDE FIXME: don't ever do this
    #             # -> TDE: you are the guy that did what we should never do in commit e6f038a
    #             order.message_partner_ids = [(4, order.partner_id.id), (3, request.website.partner_id.id)]
    #             if not errors:
    #                 return request.redirect(kw.get('callback') or '/shop/confirm_order')
    #
    #     is_public_user = request.website.is_public_user()
    #     render_values = {
    #         'website_sale_order': order,
    #         'partner_id': partner_id,
    #         'mode': mode,
    #         'checkout': values,
    #         'can_edit_vat': can_edit_vat,
    #         'error': errors,
    #         'callback': kw.get('callback'),
    #         'only_services': order and order.only_services,
    #         'account_on_checkout': request.website.account_on_checkout,
    #         'is_public_user': is_public_user,
    #         'is_public_order': order._is_public_order(),
    #         'use_same': is_public_user or ('use_same' in kw and str2bool(kw.get('use_same') or '0')),
    #     }
    #     render_values.update(self._get_country_related_render_values(kw, render_values))
    #     return request.render("website_sale.address", render_values)
