from odoo import fields , models, api,_
from odoo.exceptions import Warning
from odoo.exceptions import UserError,ValidationError
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta


class PaymentBatches(models.Model):
    _name = 'fees.payment.run'

    name = fields.Char()
    code = fields.Char()
    stage_id = fields.Many2one('education.stage')
    level_id = fields.Many2one('education.stage.year')
    class_id = fields.Many2one('education.classes')
    fees_structure = fields.Many2one('fees.rules.structure')
    batch_type = fields.Selection([('stage','Stage'),('level','Level'),('class','class')])
    fees_payment_ids = fields.One2many('fees.payment','payment_run_id')


class PaymentBatchRun(models.TransientModel):
    _name = 'fees.payment.generate'

    student_ids = fields.Many2many('student.student',string='Students')

    @api.multi
    def compute_fees(self):
        fees_payment = self.env['fees.payment']
        [data] = self.read()
        active_id = self.env.context.get('active_id')
        if active_id:
            [run_data] = self.env['fees.payment.run'].browse(active_id).read(['fees_structure','stage_id', 'level_id', 'class_id'])
        class_id = run_data.get('class_id')
        level_id = run_data.get('level_id')
        stage_id = run_data.get('stage_id')
        fees_structure = run_data.get('fees_structure')
        if not data['student_ids']:
            raise UserError(_("You must select student(s) to generate Payment(s)."))
        for student in self.env['student.student'].browse(data['student_ids']):
            # slip_data = self.env['hr.payslip'].onchange_employee_id(from_date, to_date, employee.id, contract_id=False)
            res = {
                'student_id': student.id,
                'fees_structure': fees_structure,
                'payment_run_id': active_id,
            }
            fees_payment += self.env['hr.payslip'].create(res)
        fees_payment.compute_sheet()
        return {'type': 'ir.actions.act_window_close'}


class FeesPaymentBatch(models.Model):
    _inherit = 'fees.payment'

    payment_run_id = fields.Many2one('fees.payment.run')
