from odoo import models


class OperationOrderXlsx(models.AbstractModel):
    _name = 'report.reports.report_operation_order_xlx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):

        format1 = workbook.add_format({'font_size': 13,'align': 'vcenter','bold': True})
        format2 = workbook.add_format({'font_size': 11,'align': 'vcenter'})
        sheet = workbook.add_worksheet('Operation Orders')
        sheet.set_column(0,0,20)
        sheet.set_column(1,1,20)
        sheet.set_column(2,2,20)
        sheet.set_column(3,3,20)
        sheet.set_column(4,4,20)
        sheet.set_column(5,5,20)
        sheet.set_column(6,6,20)
        sheet.set_column(7,7,20)
        sheet.set_column(8,8,20)
        sheet.set_column(9,9,20)
        sheet.set_column(10,10,20)
        sheet.set_column(11,11,20)
        sheet.set_column(12,12,20)
        """sheet.set_column(13,13,20)
        sheet.set_column(14,14,20)
        sheet.set_column(15,15,20)
        sheet.set_column(16,16,20)
        sheet.set_column(17,17,20)"""

        row = 0

        sheet.write(row, 0, 'Date', format1)
        sheet.write(row, 1, 'Contract No', format1)
        sheet.write(row, 2, 'Customer', format1)
        sheet.write(row, 3, 'Item', format1)
        sheet.write(row, 4, 'POD', format1)
        sheet.write(row, 5, 'Price', format1)
        sheet.write(row, 6, 'Contract QTY', format1)
        sheet.write(row, 7, 'Contract Amount', format1)
        sheet.write(row, 8, 'Invoice QTY', format1)
        sheet.write(row, 9, 'Invoice Amount', format1)
        sheet.write(row, 10, 'remaining QTY', format1)
        sheet.write(row, 11, 'remaining Amount', format1)
        sheet.write(row, 12, 'status', format1)
        """sheet.write(row, 13, 'Advanced Payment', format1)
        sheet.write(row, 14, 'Deduction Advanced Payment', format1)
        sheet.write(row, 15, 'Advanced Payment Balance', format1)
        sheet.write(row, 16, 'Payments', format1)
        sheet.write(row, 17, 'Due Balance', format1)"""


        for obj in lines:
            contract_qty = 0
            contract_amount = 0
            invoice_qty = 0
            invoice_amount = 0
            row = row + 1
            sheet.write(row, 0, str(obj.contract_id.date_order), format2)
            sheet.write(row, 1, obj.contract_no, format2)
            sheet.write(row, 2, obj.customer.name, format2)
            sheet.write(row, 3, obj.product.name, format2)
            sheet.write(row, 4, obj.arrival_port.name, format2)
            sheet.write(row, 5, obj.price_unit, format2)
            for rec in obj.contract_id.order_line:
                if rec.product_id == obj.product:
                    contract_qty += rec.product_uom_qty
                    contract_amount += rec.price_subtotal
            sheet.write(row, 6, contract_qty, format2)
            sheet.write(row, 7, contract_amount, format2)
            for rec in obj.invoice_id.invoice_line_ids:
                if rec.product_id == obj.product:
                    invoice_qty += rec.quantity
                    invoice_amount += rec.price_subtotal
            sheet.write(row, 8, invoice_qty, format2)
            sheet.write(row, 9, invoice_amount, format2)
            sheet.write(row, 10, contract_qty-invoice_qty, format2)
            sheet.write(row, 11, contract_amount-invoice_amount, format2)
            sheet.write(row, 12, dict(obj._fields['state'].selection).get(obj.state), format2)
            """sheet.write(row, 13, obj.invoice_id.advanced_payment, format2)
            sheet.write(row, 14, obj.invoice_id.deduction_advanced_payment, format2)
            sheet.write(row, 15, obj.invoice_id.advanced_payment-obj.invoice_id.deduction_advanced_payment, format2)
           """

