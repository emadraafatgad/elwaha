from odoo import fields, models , api

class TravelList(models.Model):
    _name = 'travel.list'
    _description = 'Travel LIst'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Number",readonly=True,default='New')
    travel_list = fields.Many2many('travel.company')
    state = fields.Selection([('new', 'new'),('done', 'Done')], default='new',track_visibility='onchange')

    @api.multi
    def action_done(self):
        for rec in self.travel_list:
            rec.state = 'done'
        self.state = 'done'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('travel.list')
        return super(TravelList, self).create(vals)

