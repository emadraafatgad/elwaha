from odoo import fields,api,models


class ClinicDiagnosis(models.Model):
    _name = 'clinic.diagnosis'

    name = fields.Char()
    appointment_id = fields.Many2one('oeh.medical.appointment')


class DiagnosisAppointment(models.Model):
    _inherit = 'oeh.medical.appointment'

    diagnosis_ids = fields.Many2many('clinic.diagnosis')
    # patient_id = fields.Many2one('oeh.medical.patient')