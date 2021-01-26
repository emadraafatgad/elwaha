# from extra.master_data.models.interpol_request import InterpolRequest
from odoo import fields, models , api,_
from datetime import date
from dateutil.relativedelta import relativedelta

class ClearanceList(models.Model):
    _name = 'clearance.list'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    state = fields.Selection([('new','New'),('confirmed','Confirmed')],default='new',track_visibility="onchange")
    name = fields.Char(string="Number",readonly=True,default='New')
    assign_date = fields.Date()
    receive_date = fields.Date()
    clearance_list = fields.Many2many('labor.clearance')

    @api.multi
    def action_confirm(self):
        self.receive_date = date.today()
        for rec in self.clearance_list:
            rec.state='confirmed'
        self.state = 'confirmed'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('clearance.list')
        vals['assign_date'] = date.today()
        return super(ClearanceList, self).create(vals)

