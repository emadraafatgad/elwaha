from odoo import fields,models,api
import time


class ClinicPrescription(models.Model):
    _name = 'oeh.medical.prescriptions'
    _inherit = ['mail.thread']

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

    name = fields.Char()
    patient_id = fields.Many2one('oeh.medical.patient')
    doctor_id = fields.Many2one('oeh.medical.physician',default=_get_physician)
    prescription_date = fields.Date(default=lambda *a: time.strftime('%Y-%m-%d'))
    service_id = fields.Many2one('oeh.medical.service')
    appointment_id = fields.Many2one('oeh.medical.appointment')
    prescription_line_ids = fields.One2many('oeh.medical.prescriptions.line','prescription_id')
    medicine_id = fields.Many2one('oeh.medical.medicine')

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('oeh.medical.prescriptions')
        vals['name'] = sequence
        return super(ClinicPrescription, self).create(vals)


class ClinicPrescriptionLine(models.Model):
    _name = 'oeh.medical.prescriptions.line'

    medicine_id = fields.Many2one('oeh.medical.medicine')
    qty = fields.Integer()
    form = fields.Many2one('oeh.medical.medicine.form')
    dose = fields.Integer()
    days = fields.Integer()
    frequency = fields.Many2one('oeh.medical.medicine.frequency')
    note = fields.Text()
    prescription_id = fields.Many2one('oeh.medical.prescriptions')


class FrequencyPrescription(models.Model):
    _name = 'oeh.medical.medicine.frequency'

    name = fields.Char()