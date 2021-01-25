from odoo import fields, models,api,_
from datetime import date

from odoo.exceptions import ValidationError


class InterpolBroker(models.Model):
    _name = 'interpol.broker'
    _description = 'Interpol Broker Assign'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Number",readonly=True,default='New')
    broker = fields.Many2one('res.partner',required=True,domain=[('vendor_type','=','interpol_broker')])
    assign_date = fields.Date(default=date.today())
    interpol_request = fields.Many2many('interpol.request', string='Interpol Requests',required=True)
    state = fields.Selection([('new', 'new'), ('assigned', 'Assigned'), ('partially_done', 'Partially Done'), ('done', 'Done')], default='new', track_visibility="onchange")
    list_total_count = fields.Integer(compute='_compute_value')
    done_count = fields.Integer(compute='_compute_value')
    remaining_count = fields.Integer(compute='_compute_value')

    @api.one
    @api.depends('interpol_request')
    def _compute_value(self):
        self.list_total_count = len(self.interpol_request)
        self.done_count = len([rec for rec in self.interpol_request if rec.state == 'done'])
        self.remaining_count = len([rec for rec in self.interpol_request if rec.state != 'done'])

    @api.multi
    def action_assign(self):
        for list in self.interpol_request:
            list.state= 'assigned'
            list.end_date= self.assign_date
        self.state = 'assigned'

    @api.constrains('broker')
    def const_broker_list(self):
        for rec in self.interpol_request:
            rec.broker_list_id = self.id

    def _get_product_default(self):

        product = self.env['product.recruitment.config'].search([('type', '=', 'interpol')])
        self.product = product.product

    product = fields.Many2one('product.product',compute=_get_product_default)

    @api.multi
    def action_confirm(self):
        invoice_line = []
        purchase_journal = self.env['account.journal'].search([('type', '=', 'purchase')])[0]
        accounts = self.product.product_tmpl_id.get_product_accounts()
        if all(l.interpol_no and l.attachment for l in self.interpol_request):
            self.state = 'done'
        else:
            self.state = 'partially_done'
        for list in self.interpol_request:
            if any([(not list.interpol_no or not list.attachment) and list.state == 'assigned']):
                raise ValidationError(_('You must enter interpol info'))
            if any([list.interpol_no and list.attachment and list.state == 'assigned']):
               list.interpol_request_done()

               invoice_line.append((0, 0, {
                   'product_id': list.product.id,
                   'name': list.labor,
                   'uom_id': list.product.uom_id.id,
                   'price_unit': list.product.list_price,
                   'discount': 0.0,
                   'quantity': 1,
                   'account_id': accounts.get('stock_input') and accounts['stock_input'].id or \
                                 accounts['expense'].id,
               }))

               self.env['account.invoice'].create({
                   'partner_id': self.broker.id,
                   'state': 'draft',
                   'type': 'in_invoice',
                   'origin': self.name,
                   'journal_id': purchase_journal.id,
                   'account_id': self.broker.property_account_payable_id.id,
                   'invoice_line_ids': invoice_line,

               })

               return {
                   'name': _('Interpol List Invoice'),
                   'view_type': 'form',
                   'view_mode': 'tree,form',
                   'res_model': 'account.invoice',
                   'type': 'ir.actions.act_window',
                   'domain': [('origin', '=', self.name)]

               }

    @api.constrains('broker')
    def const_broker(self):
        for rec in self.interpol_request:
            rec.broker = self.broker

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('interpol.broker')

        return super(InterpolBroker, self).create(vals)


class InterpolAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        origin = self.env['interpol.broker'].search([('name', '=', self.origin)])
        for list in origin.interpol_request:
            list.invoice_id = self.id

        return super(InterpolAccountInvoice, self).action_invoice_open()



