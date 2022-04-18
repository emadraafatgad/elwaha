from odoo import http
from odoo.http import request


class Bulx(http.Controller):
    @http.route('/bulx/create-product',type='json', auth='public')
    def bulx_create_product(self, **rec):
        product = request.env['product.product'].sudo().create({'name':rec['name'],'type':rec['product_type']})
        return {'status':200, 'message':product.name + " success" }

    @http.route('/bulx/create-category', type='json', auth='public')
    def bulx_create_category(self, **rec):
        category = request.env['product.category'].sudo().create({'name': rec['name']})
        return {'status': 200, 'message': category.name + " success"}

    @http.route('/bulx/create-brand', type='json', auth='public')
    def bulx_create_category(self, **rec):
        brand = request.env['product.brand'].sudo().create({'name': rec['name']})
        return {'status': 200, 'message': brand.name + " success"}

    @http.route('/bulx/create-product', type='json', auth='public')
    def bulx_create_product(self, **rec):
        product = request.env['product.product'].sudo().create({'name': rec['name'], 'type': rec['product_type']})
        return {'status': 200, 'message': product.name + " success"}





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