# -*- coding: utf-8 -*-
from odoo import http

# class WahaDiscountv12(http.Controller):
#     @http.route('/waha_discountv12/waha_discountv12/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/waha_discountv12/waha_discountv12/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('waha_discountv12.listing', {
#             'root': '/waha_discountv12/waha_discountv12',
#             'objects': http.request.env['waha_discountv12.waha_discountv12'].search([]),
#         })

#     @http.route('/waha_discountv12/waha_discountv12/objects/<model("waha_discountv12.waha_discountv12"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('waha_discountv12.object', {
#             'object': obj
#         })