import datetime
from datetime import date, datetime
from datetime import timedelta
import logging
import pytz
from requests import help

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.translate import _


class ClinicAppointment(models.Model):
    _inherit = 'oeh.medical.appointment'



    @api.multi
    def open_specific_session(self):
        self.ensure_one()
        session_id = self.env['oeh.medical.service'].search([('patient_id','=',self.patient.id),
                                                             ('state','!=','Completed')],limit=1)
        if not session_id :
            return self.open_patient_session()
        else:
            return {
                "type": "ir.actions.act_window",
                "res_model": "oeh.medical.service",
                "views": [[False, "form"]],
                "res_id": session_id.id,
                }

    def open_patient_session(self):
        self.ensure_one()
        view = self.env.ref('clinic.oeh_medical_service_form')
        print(view, "10000000")
        ctx = dict()
        ctx.update({
            'default_patient_id': self.patient.id,
            'default_clinic_id': self.clinic.id,
            'default_doctor_id':self.doctor.id,
            'default_service_date': self.appointment_date,

        })
        return {
            # 'domain': "[('id','=', " + str(resr_id.id) + ")]",
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view.id,
            'res_model': 'oeh.medical.service',
            'target': 'current',
            'type': 'ir.actions.act_window',
            'context': ctx,

        }
