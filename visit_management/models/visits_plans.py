from odoo import models, fields, api, tools, exceptions, _


class VisitsClass(models.Model):
    _name = 'visit.plan'
    _rec_name = 'employee_id'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    class_id = fields.Many2one('visit.class',track_visibility='onchange')
    count = fields.Integer(required=True,track_visibility='onchange')
    date_from = fields.Date(required=True,readonly=False,track_visibility='onchange')
    date_to = fields.Date(required=True,readonly=False,track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee',required=True,track_visibility='onchange')
    customer_id = fields.Many2one('res.partner',domain="[('customer','=',True),('class_id','=',class_id)]")
    class_plan_id = fields.Many2one('class.plan',track_visibility='onchange')

    # @api.depends('class_plan_id')
    # def get_dates(self):
    #     for rec in self:
    #         if rec.class_plan_id:
    #             rec.date_from = rec.class_plan_id.start_date
    #             rec.date_to = rec.class_plan_id.end_date


class EmployeeVisits(models.Model):
    _inherit = 'hr.employee'

    visits_plan_ids = fields.One2many('customer.visit','employee_id')
    customer_ids = fields.Many2many('res.partner',string="Doctors", domain="[('customer','=',True),('class_id','!=',False)]")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    class_id = fields.Many2one('visit.class')
    # employee_id = fields.Many2one('hr.employee')
