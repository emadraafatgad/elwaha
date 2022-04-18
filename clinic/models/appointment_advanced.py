from odoo import api, models,fields,_


class AppointmentAdvanced(models.Model):
    _inherit = 'oeh.medical.appointment'

    # @api.onchange('evaluation_ids')
    # def add_eval_patients_doctor(self):
    #     print("EvaVAVAADVADVADCADVADVSDV+++++++++++++++=")
    #     for evaluation_id in self.evaluation_ids:
    #         evaluation_id.update({'patient_id': self.patient.id,
    #                               'doctor_id': self.doctor.id})

    @api.onchange('prescription_ids')
    def add_presc_patients_doctor(self):
        print("HERE WE GOOO")
        for prescription_id in self.prescription_ids:
            prescription_id.update({'patient_id': self.patient.id,
                                   'doctor_id': self.doctor.id})


    # @api.onchange('')
    # def add_patients_doctor(self):
    #     for evaluation_id in self.evaluation_ids:
    #         evaluation_id.patient_id = self.patient
    #         evaluation_id.doctor_id = self.doctor
