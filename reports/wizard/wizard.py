from odoo import models, fields, api, _
from datetime import date
from dateutil.relativedelta import relativedelta
import xlwt
import base64
from io import BytesIO


class WizardContractReport(models.TransientModel):
    _name = 'wizard.contract.report'
    _description = 'Contract Report'

    @api.multi
    def _get_first_day(self):
        today = date.today()
        first_day = today.replace(day=1)
        if today.day > 25:
            return (first_day + relativedelta(months=1))
        else:
            return (first_day)

    date_from = fields.Date(string="From Date",required=True,store=True,default=_get_first_day)
    date_to = fields.Date("To Date", required=True,store=True, default=date.today())
    report_file = fields.Binary('Contract Report')
    file_name = fields.Char('File Name')
    printed = fields.Boolean('Report Printed')


    @api.multi
    def action_contract_report(self):

        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Contract Report')
        column_heading_style = xlwt.easyxf('font:height 200;font:bold True;')
        row = 2
        for wizard in self:
            report_head = 'Contract Report'
            if wizard.date_from and wizard.date_to:
                report_head += ' From  ( ' + str(wizard.date_from) + ' ) ' + ' To  ( ' + str(wizard.date_to) + ')'
            worksheet.write_merge(0, 0, 0, 2, report_head, xlwt.easyxf(
                'font:height 300; align: vertical center; align: horiz center;pattern: pattern solid, fore_color black; font: color white; font:bold True;' "borders: top thin,bottom thin"))
            worksheet.col(0).width = 5000
            worksheet.col(1).width = 10000
            worksheet.col(2).width = 5000
            worksheet.col(3).width = 5000
            worksheet.col(4).width = 5000
            worksheet.col(5).width = 5000
            worksheet.col(6).width = 5000
            worksheet.col(7).width = 5000
            worksheet.col(8).width = 5000
            worksheet.col(9).width = 5000
            worksheet.col(10).width = 5000
            worksheet.col(11).width = 5000
            worksheet.col(12).width = 5000
            worksheet.col(13).width = 5000
            worksheet.row(0).height = 500
            worksheet.write(1, 0, _('Date'), column_heading_style)
            worksheet.write(1, 1, _('Contract No'), column_heading_style)
            worksheet.write(1, 2, _('Customer'), column_heading_style)
            worksheet.write(1, 3, _('Item'), column_heading_style)
            worksheet.write(1, 4, _('POD'), column_heading_style)
            worksheet.write(1, 5, _('Price'), column_heading_style)
            worksheet.write(1, 6, _('Contract QTY'), column_heading_style)
            worksheet.write(1, 7, _('Contract Amount'), column_heading_style)
            worksheet.write(1, 8, _('Invoice QTY'), column_heading_style)
            worksheet.write(1, 9, _('Invoice Amount'), column_heading_style)
            worksheet.write(1, 10, _('remaining QTY'), column_heading_style)
            worksheet.write(1, 11, _('remaining Amount'), column_heading_style)
            worksheet.write(1, 12, _('status'), column_heading_style)
            worksheet.write(1, 13, _('Advanced Payment'), column_heading_style)
            values = self.env['operation.order'].search([('contract_date', '>=', wizard.date_from),('contract_date', '<=', wizard.date_to)])

            for rec in values:
                contract_qty = 0
                contract_amount = 0
                invoice_qty = 0
                invoice_amount = 0
                worksheet.write(row, 0, str(rec.contract_id.date_order))
                worksheet.write(row, 1, rec.contract_no)
                worksheet.write(row, 2, rec.customer.name)
                worksheet.write(row, 3, rec.product.name)
                worksheet.write(row, 4, rec.arrival_port.name)
                worksheet.write(row, 5, rec.price_unit)
                for record in rec.contract_id.order_line:
                    if record.product_id == rec.product:
                        contract_qty += record.product_uom_qty
                        contract_amount += record.price_subtotal
                worksheet.write(row, 6, contract_qty)
                worksheet.write(row, 7, contract_amount)
                for record in rec.invoice_id.invoice_line_ids:
                    if record.product_id == rec.product:
                        invoice_qty += record.quantity
                        invoice_amount += record.price_subtotal
                worksheet.write(row, 8, invoice_qty)
                worksheet.write(row, 9, invoice_amount)
                worksheet.write(row, 10, contract_qty-invoice_qty)
                worksheet.write(row, 11, contract_amount-invoice_amount)
                worksheet.write(row, 12, dict(rec._fields['state'].selection).get(rec.state))
                worksheet.write(row, 13, rec.invoice_id.advanced_payment)
                row += 1

            fp = BytesIO()
            workbook.save(fp)
            excel_file = base64.encodestring(fp.getvalue())
            wizard.report_file = excel_file
            wizard.file_name = 'Contract Report.xls'
            wizard.printed = True
            fp.close()
            return {
                'view_mode': 'form',
                'res_id': wizard.id,
                'res_model': 'wizard.contract.report',
                'view_type': 'form',
                'type': 'ir.actions.act_window',
                'context': self.env.context,
                'target': 'new',
            }

