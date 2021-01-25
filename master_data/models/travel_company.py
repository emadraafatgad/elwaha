from odoo import fields, models , api
from datetime import date
from dateutil.relativedelta import relativedelta


class TravelCompany(models.Model):
    _name = 'travel.company'
    _description = 'Travel Company'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Number",readonly=True,default='New')
    labor_id = fields.Many2one('labor.profile')
    invoice = fields.Char()
    passport_no = fields.Char()
    destination_city = fields.Char()
    reservation_no = fields.Char()
    agency_code = fields.Char()
    agency = fields.Many2one('res.partner',domain=[('agency','=',True)])
    state = fields.Selection([('new', 'new'),('done', 'Done')], default='new',track_visibility='onchange')



    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('travel.company')
        return super(TravelCompany, self).create(vals)

