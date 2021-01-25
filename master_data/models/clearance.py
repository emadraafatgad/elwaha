# from extra.master_data.models.interpol_request import InterpolRequest
from odoo import fields, models , api,_
from datetime import date
from dateutil.relativedelta import relativedelta

class LaborClearance(models.Model):
    _name = 'labor.clearance'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    state = fields.Selection([('new','New'),('confirmed','Confirmed')],default='new',track_visibility="onchange")
    name = fields.Char(string="Number",readonly=True,default='New')
    labor_id = fields.Many2one('labor.profile')
    labor_name = fields.Many2one('labor.profile')
    agency = fields.Many2one('res.partner',domain=[('agency','=',True)])
    lc1 = fields.Many2one('labor.village')
    lc2 = fields.Many2one('labor.parish')
    lc3 = fields.Many2one('labor.subcounty')
    district = fields.Many2one('labor.district')
    job_title = fields.Selection([('house_maid', 'House Maid'), ('pro_maid', 'Pro Maid'),('pro_worker','Pro Worker')])
    gender = fields.Selection([('Male', 'Male'), ('Female', 'Female'),])
    contact = fields.Char()
    passport_no = fields.Char()

    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('labor.clearance')
        return super(LaborClearance, self).create(vals)


