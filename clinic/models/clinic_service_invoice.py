from odoo import api, models, fields


class ClinicServiceInvoice(models.Model):
    _inherit='oeh.medical.service'

    def start_session_service(self):
        for rec in self:
            print("start")
            complete_sessions = rec.completed_sessions + 1
            rec.completed_sessions = complete_sessions
            rec.total_cost = complete_sessions * rec.cost
            # self.move_medicine_to_inventory()
            rec.send_stock_req()
            if not rec.is_package and complete_sessions > rec.package_sessions:
                rec.action_service_invoice_create()
                rec.state = 'In Progress'

    @api.multi
    def _default_account(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        return journal.default_credit_account_id.id

    def action_service_invoice_create(self):
        invoice_obj = self.env["account.invoice"]
        invoice_line_obj = self.env["account.invoice.line"]
        inv_ids = []
        for acc in self:
            # Create Invoice
            if acc.patient_id:
                curr_invoice = {
                    'partner_id': acc.patient_id.partner_id.id,
                    'patient': acc.patient_id.id,
                    'account_id': acc.patient_id.partner_id.property_account_receivable_id.id,
                    'state': 'draft',
                    'type': 'out_invoice',
                    'date_invoice': acc.service_date,
                    'origin': "Service # : " + acc.name,
                }

                inv_ids = invoice_obj.create(curr_invoice)
                inv_id = inv_ids.id

                if inv_ids:
                    prd_account_id = self._default_account()
                    # Create Invoice line
                    curr_invoice_line = {
                        'name': "Consultancy invoice for " + acc.patient_id.name,
                        'price_unit': acc.cost,
                        'quantity': 1,
                        'account_id': prd_account_id,
                        'invoice_id': inv_id,
                    }
                    inv_line_ids = invoice_line_obj.create(curr_invoice_line)
                # inv_ids.compute_taxes()

        return True
