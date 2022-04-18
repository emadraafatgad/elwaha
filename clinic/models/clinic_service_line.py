from odoo import fields, api, models


class ClinicServiceLine(models.Model):
    _name = 'oeh.medical.service.line'

    name = fields.Char(string='Name', required=True)
    session_cost = fields.Integer(string="Session Price", required=True)
    machine_ids = fields.Many2many('oeh.medical.machine')
    medicine_value_ids = fields.One2many('oeh.medical.medicine.value','service_line_id')
    service_type_id = fields.Many2one("oeh.medical.service.type" ,required=True)
    clinic_type = fields.Selection([('nutrition', 'Nutrition clinic'), ('beauty', 'Beauty Clinic')], default="beauty")
    # @api.model
    # def create(self, vals):
    #     sequence = self.env['ir.sequence'].next_by_code('oeh.medical.service.ine')
    #     vals['code'] = sequence
    #     return super(ClinicServiceLine, self).create(vals)
    #

class ClinicServiceType(models.Model):
    _name = "oeh.medical.service.type"

    name = fields.Char(required=True)
