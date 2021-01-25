from odoo import fields, api, models,_
from odoo.exceptions import ValidationError
from datetime import  date


# class RecruitmentManagement(models.Model):
#     _name = 'recruitment.management'
#
#     name = fields.Char(readonly=True)
#
#     slave_id = fields.Many2one('res.partner',domain="[('is_slave','=',True),('pre_medical_check','=','Fit')]")
#     date = fields.Date('Registration Date',date.today())
#     passport_state = fields.Selection()
#     training_state = fields.Selection()
#     interpol_state = fields.Selection()
# class ResPartner(models.Model):
#     _inherit = "res.partner"
#
#     training_center = fields.Boolean()
#



class TrainingCenter(models.Model):
    _name = 'training.center'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _inherits = {
        'res.partner': 'partner_id',
    }
    _description = 'Labor Profile'

    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='cascade',
                                 help='Partner-related data of the patient')

    @api.model
    def create(self, vals):
        vals['training_center'] = True
        vals['supplier'] = True
        vals['company_type'] = 'company'
        labor = super(TrainingCenter, self).create(vals)
        return labor


class SlaveTraining(models.Model):
    _name = 'slave.training'
    _description = 'Training'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    name = fields.Char(readonly=True)
    slave_id = fields.Many2one('labor.profile',string="Labor", domain="[('pre_medical_check','=','Fit')]")
    start_date = fields.Date(readonly=True)
    end_date = fields.Date(readonly=True)
    state = fields.Selection([('new', 'New'), ('in_progress', 'Inprogress'), ('finished', 'Finished')], default='new')
    training_center_id = fields.Many2one('training.center')
    note = fields.Text()

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('slave.training')
        vals['name'] = sequence
        return super(SlaveTraining, self).create(vals)

class TrainingList(models.Model):
    _name = 'training.list'
    _description = 'Training List'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    name= fields.Char('Sequence',default='New',readonly=True)
    state = fields.Selection([('new', 'New'), ('in_progress', 'Inprogress'), ('finished', 'Finished')],default='new',track_visibility="onchange")
    start_date = fields.Date(track_visibility="onchange")
    end_date = fields.Date(track_visibility="onchange")
    training_center = fields.Many2one('training.center',track_visibility="onchange")
    training_requests = fields.Many2many('slave.training')

    def _get_product_default(self):
        product = self.env['product.recruitment.config'].search([('type', '=', 'training')])
        for rec in self:
            rec.product = product.product

    product = fields.Many2one('product.product', compute=_get_product_default)

    @api.constrains('training_requests')
    def constrain_training_requests(self):
        for rec in self.training_requests:
            rec.training_center_id = self.training_center

    show = fields.Boolean()
    bill_count = fields.Integer(compute='_compute_bill', string='Bill', default=0)
    bill_ids = fields.Many2many('account.invoice', compute='_compute_bill', string='Bill', copy=False)

    def action_view_bill(self):
        action = self.env.ref('purchase.action_invoice_pending')
        result = action.read()[0]
        result.pop('id', None)
        result['context'] = {}
        b_ids = sum([line.bill_ids.ids for line in self], [])
        if len(b_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, b_ids)) + "])]"
        elif len(b_ids) == 1:
            res = self.env.ref('account.invoice_supplier_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = b_ids and b_ids[0] or False
        return result

    def _compute_bill(self):
        for line in self:
            bills = self.env['account.invoice'].search([
                ('origin', '=', self.name)
            ])
            line.bill_ids = bills
            line.bill_count = len(bills)

    @api.multi
    def action_start(self):
        if not self.training_center:
            raise ValidationError(_('you must enter training center'))
        self.start_date = date.today()
        for rec in self.training_requests:
            rec.state = 'in_progress'
            rec.start_date = self.start_date
        self.state = 'in_progress'

    @api.multi
    def action_finish(self):
        self.end_date = date.today()
        self.state = 'finished'


    @api.multi
    def create_bill(self):
        invoice_line = []
        purchase_journal = self.env['account.journal'].search([('type', '=', 'purchase')])[0]
        accounts = self.product.product_tmpl_id.get_product_accounts()
        description = ''
        for rec in self.training_requests:
            description += rec.slave_id.name + ','
        invoice_line.append((0, 0, {
            'product_id': self.product.id,
            'name': description,
            'uom_id': self.product.uom_id.id,
            'price_unit': self.training_center.cost,
            'discount': 0.0,
            'quantity': len(self.training_requests),
            'account_id': accounts.get('stock_input') and accounts['stock_input'].id or \
                          accounts['expense'].id,
        }))
        self.env['account.invoice'].create({
            'partner_id': self.training_center.id,
            'state': 'draft',
            'type': 'in_invoice',
            'origin': self.name,
            'journal_id': purchase_journal.id,
            'account_id': self.training_center.property_account_payable_id.id,
            'invoice_line_ids': invoice_line,

        })
        self.show = True

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('training.list')
        vals['name'] = sequence
        return super(TrainingList, self).create(vals)
