# -*- coding: utf-8 -*-
# from odoo import http


# class PurchaseTemplate(http.Controller):
#     @http.route('/purchase_template/purchase_template', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_template/purchase_template/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_template.listing', {
#             'root': '/purchase_template/purchase_template',
#             'objects': http.request.env['purchase_template.purchase_template'].search([]),
#         })

#     @http.route('/purchase_template/purchase_template/objects/<model("purchase_template.purchase_template"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_template.object', {
#             'object': obj
#         })
