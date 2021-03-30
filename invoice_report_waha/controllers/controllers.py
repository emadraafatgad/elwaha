# -*- coding: utf-8 -*-
from odoo import http

# class InvoiceReportWaha(http.Controller):
#     @http.route('/invoice_report_waha/invoice_report_waha/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_report_waha/invoice_report_waha/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_report_waha.listing', {
#             'root': '/invoice_report_waha/invoice_report_waha',
#             'objects': http.request.env['invoice_report_waha.invoice_report_waha'].search([]),
#         })

#     @http.route('/invoice_report_waha/invoice_report_waha/objects/<model("invoice_report_waha.invoice_report_waha"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_report_waha.object', {
#             'object': obj
#         })