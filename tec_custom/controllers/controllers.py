# -*- coding: utf-8 -*-
# from odoo import http


# class TecCustom(http.Controller):
#     @http.route('/tec_custom/tec_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tec_custom/tec_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('tec_custom.listing', {
#             'root': '/tec_custom/tec_custom',
#             'objects': http.request.env['tec_custom.tec_custom'].search([]),
#         })

#     @http.route('/tec_custom/tec_custom/objects/<model("tec_custom.tec_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tec_custom.object', {
#             'object': obj
#         })
