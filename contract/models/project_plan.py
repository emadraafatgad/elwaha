from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from datetime import  date


class PurchaseProjectPlan(models.Model):
    _name = 'purchase.project.plan'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Project Plan'

    name = fields.Char(string="Project Name", required=True)
    line_ids = fields.One2many('purchase.project.line','plan_id')
    company_id = fields.Many2one('res.company', 'Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    description = fields.Char()
    planned_date = fields.Date()
    priority = fields.Selection(
        selection=[
            ('0', 'Low'),
            ('1', 'Normal'),
            ('2', 'High')],string='Priority',default='1',)
    state = fields.Selection([
        ('new', 'New'),
        ('done', 'Confirmed')],default='new')
    budget = fields.Monetary()
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)

    @api.multi
    def confirm_plan(self):
        self.ensure_one()
        self.state = 'done'


class PurchaseProjectLine(models.Model):
    _name = 'purchase.project.line'

    plan_id = fields.Many2one('purchase.project.plan')
    description= fields.Char(required=True)
    contractor = fields.Char()
    comment = fields.Char()
    type_of_procurement = fields.Char()
    planned_amount = fields.Float(required=True)
    actual_amount = fields.Float(required=True)
    estimated_date = fields.Date()
