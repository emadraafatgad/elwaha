# -*- coding: utf-8 -*-
from odoo import http

# class Elwafa(http.Controller):
#     @http.route('/elwafa/elwafa/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/elwafa/elwafa/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('elwafa.listing', {
#             'root': '/elwafa/elwafa',
#             'objects': http.request.env['elwafa.elwafa'].search([]),
#         })

#     @http.route('/elwafa/elwafa/objects/<model("elwafa.elwafa"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('elwafa.object', {
#             'object': obj
#         })