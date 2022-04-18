from odoo import api , fields, models ,_


class ServiceMachineLine(models.Model):
    _name = 'oeh.medical.service.machine'

    machine_id = fields.Many2one('oeh.medical.machine')
    service_id = fields.Many2one('oeh.medical.service.line')
#
# class ServiceMachineLine(models.Model):
#     _name = 'oeh.medical.service.medicine'
#
#     name = fields.Many2one('oeh.medical.machine')
#     service_id = fields.Many2one('oeh.medical.service.line')
