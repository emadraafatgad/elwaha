from odoo import fields, models,api,_
from datetime import date
from odoo.exceptions import ValidationError


class PassportBroker(models.Model):
    _name = 'passport.broker'
    _description = 'Passport Broker Assign'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    name= fields.Char('sequence',default='New')
    broker = fields.Many2one('res.partner',required=True,domain=[('vendor_type','=','passport_broker')])
    assign_date = fields.Date(default=date.today())
    deadline = fields.Date()
    passport_request = fields.Many2many('passport.request', string='Passport Requests',required=True)
    state = fields.Selection([('new', 'new'), ('assigned', 'Assigned'),('confirmed', 'Confirmed')], default='new', track_visibility="onchange")
    list_total_count = fields.Integer(compute='_compute_value')
    done_count = fields.Integer(compute='_compute_value')
    remaining_count = fields.Integer(compute='_compute_value')

    @api.one
    @api.depends('passport_request')
    def _compute_value(self):
        self.list_total_count = len(self.passport_request)
        self.done_count = len([rec for rec in self.passport_request if rec.state == 'done'])
        self.remaining_count = len([rec for rec in self.passport_request if rec.state != 'done'])

    @api.constrains('broker')
    def const_broker_list(self):
        for rec in self.passport_request:
            rec.broker_list_id = self.id

    @api.multi
    def action_assign(self):
        for list in self.passport_request:
            list.state= 'releasing'
            list.end_date= self.assign_date
            list.broker = self.broker
        self.state = 'assigned'

    @api.multi
    def action_confirm(self):
        for list in self.passport_request:
            if list.passport_no and list.pass_start_date and list.pass_end_date and list.pass_from:
               list.request_passport_done()
               list.labor_id.request_interpol()
               list.labor_id.big_medical_request()
               list.labor_id.specify_agency_request()
            else:
                raise ValidationError(_('You must enter passport information to all list'))
        self.state = 'confirmed'

    @api.onchange('passport_request')
    def default(self):
        next_sequence = 1
        for list in self.passport_request:
            list.seq = next_sequence
            list.row_num = str(list.seq) + "/" + str(len(self.passport_request))
            next_sequence += 1

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('passport.broker')

        return super(PassportBroker, self).create(vals)