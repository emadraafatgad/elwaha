from odoo import models, fields, api, tools, exceptions, _
from odoo.exceptions import Warning, UserError


class ClassesForClients(models.Model):
    _name = 'visit.class'

    name = fields.Char()
    count = fields.Integer()


class ClassLines(models.Model):
    _name = 'class.line'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    class_id = fields.Many2one('visit.class',required=True)
    count = fields.Integer(required=True)
    done_count = fields.Integer(readonly=False)
    remain_count = fields.Integer(readonly=True,compute='get_remain_count',store=True)

    plan_id = fields.Many2one('class.plan')

    @api.depends('done_count','count')
    def get_remain_count(self):
        for line in self:
            line.remain_count = line.count - line.done_count


class ClassPlans(models.Model):
    _name = 'class.plan'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char()
    start_date = fields.Date()
    end_date = fields.Date()
    class_line_ids = fields.One2many('class.line','plan_id')
    note = fields.Char()

    # @api.onchange('start_date', 'end_date')
    # def check_date_date(self):
    #         if self.end_date and self.start_date and self.end_date < self.start_date:
    #             raise Warning(_("Invalid Dates ,Start Date must be before than End Date"))

    @api.constrains('start_date', 'end_date')
    def check_date_constrain(self):
        for rec in self:
            if rec.end_date < rec.start_date:
                raise Warning(_("Invalid Dates ,Start Date must be before than End Date"))


# class ClassLines(models.Model):
#     _inherit= 'class.line'
#
