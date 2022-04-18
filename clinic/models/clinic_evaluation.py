from odoo import api,models,fields
import time


class PatientEvaluation(models.Model):
    _name = 'oeh.medical.evaluation'
    _inherit = ['mail.thread']

    _description = " every patient need Evaluation for his visit"

    @api.multi
    def _get_physician(self):
        """Return default physician value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    doctor_id = fields.Many2one('oeh.medical.physician',default=_get_physician)
    name = fields.Char()
    patient_id = fields.Many2one('oeh.medical.patient',string="Patient")
    evaluation_name_ids = fields.One2many('clinic.evaluation','evaluation_id')
    service_id = fields.Many2one('oeh.medical.service')
    appointment_id = fields.Many2one('oeh.medical.appointment')
    eval_date = fields.Date(default=lambda *a: time.strftime('%Y-%m-%d'))
    note = fields.Text()

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('oeh.medical.evaluation')
        vals['name'] = sequence
        return super(PatientEvaluation, self).create(vals)


class ClinicEvaluation(models.Model):
    _name = 'clinic.evaluation'
    _inherit = ['mail.thread']

    name = fields.Many2one('name.evaluation',string='Evaluation',required=True)
    patient_id = fields.Many2one('oeh.medical.patient')
    appointment_id = fields.Many2one('oeh.medical.appointment')
    evaluation_id = fields.Many2one('oeh.medical.evaluation')


class NameEvaluation(models.Model):
    _name = 'name.evaluation'

    name = fields.Text('Evaluation')


class AccountInvoiceEvaluation(models.Model):
    _inherit = 'account.invoice'

    evaluation_id = fields.Many2one('oeh.medical.evaluation', string='Related Evaluation',
                                     help="related reason for this invoice")

