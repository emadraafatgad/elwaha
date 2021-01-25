from odoo import fields, models , api,_
from datetime import date


class NiraBroker(models.Model):
    _name = 'nira.broker'
    _description = 'Nira Broker List'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char('Sequence',default="New",size=256,readonly=True)
    assign_date = fields.Date(readonly=True)
    broker = fields.Many2one('res.partner',domain=[('vendor_type','=','agent')])
    nira_request = fields.Many2many('nira.letter.request')
    state = fields.Selection([('new', 'new'), ('assigned', 'Assigned'),('done', 'Done')], default='new', track_visibility="onchange")
    list_total_count = fields.Integer(compute='_compute_value')
    done_count = fields.Integer(compute='_compute_value')
    remaining_count = fields.Integer(compute='_compute_value')
    rejected_count = fields.Integer(compute='_compute_value')

    @api.model
    def _get_request_same_agent(self):
        request = self.env['nira.letter.request'].search(
            [('labourer_id.agent', '=', self.broker.id), ('state', '=', 'new')])
        t = []
        for line in request:
            t.append(line.id)
        return t

    @api.onchange('broker')
    def get_domain(self):
        if self.broker:
            get_same_agent = self._get_request_same_agent()
            domain = {'nira_request': [('id', 'in', get_same_agent)]}

            return {'domain': domain}
        else:
            domain = {'nira_request': [('id', '=', False)]}
            return {'domain': domain}

    @api.one
    @api.depends('nira_request')
    def _compute_value(self):
        self.list_total_count = len(self.nira_request)
        self.done_count = len([rec for rec in self.nira_request if rec.state == 'done'])
        self.remaining_count = len([rec for rec in self.nira_request if rec.state not in ('done','rejected')])
        self.rejected_count = len([rec for rec in self.nira_request if rec.state == 'rejected'])

    @api.multi
    def nira_assign(self):
        self.assign_date = date.today()
        for rec in self.nira_request:
            rec.delivery_date = self.assign_date
            rec.state= 'releasing'
        return self.write({'state': 'assigned'})

    @api.constrains('broker')
    def const_broker_list(self):
        for rec in self.nira_request:
            rec.broker_list_id = self.id
            rec.broker = self.broker.id

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('nira.broker')
        return super(NiraBroker, self).create(vals)



