# from extra.master_data.models.interpol_request import InterpolRequest
from odoo import fields, models , api,_
from datetime import date
from dateutil.relativedelta import relativedelta

class BigMedical(models.Model):
    _name = 'big.medical'
    _description = 'Big Medical'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Number",readonly=True,default='New')
    labor_id = fields.Many2one('labor.profile')
    gcc = fields.Many2one('res.partner',domain=[('vendor_type','=','gcc')])
    labor = fields.Char('Labor Name')
    state = fields.Selection([('new', 'New'),('gcc', 'GCC'),('hospital','Hospital'),('done', 'Done')], default='new', track_visibility="onchange")
    national_id = fields.Char(size=14,required=True,string='National ID')
    passport_no = fields.Char()
    hospital = fields.Many2one('res.partner', domain=[('vendor_type','=','hospital')],track_visibility="onchange")
    booking_date = fields.Date(track_visibility='onchange')
    check_date = fields.Date(track_visibility='onchange')
    medical_check = fields.Selection([('fit', 'Fit'),('unfit', 'Unfit'),('pending', 'Pending')],string='Result',default='pending',track_visibility="onchange")
    reason =fields.Char()
    deadline =fields.Date(track_visibility='onchange')

    def _get_product_default(self):
        product = self.env['product.recruitment.config'].search([('type', '=', 'gcc')])
        self.product = product.product

    product = fields.Many2one('product.product', compute=_get_product_default)

    def _get_product_hospital_default(self):
        product_hospital = self.env['product.recruitment.config'].search([('type', '=', 'hospital')])
        self.product_hospital = product_hospital.product

    product_hospital = fields.Many2one('product.product', compute=_get_product_hospital_default)

    @api.onchange('check_date')
    def onchange_check_date(self):
        if self.check_date:
            self.deadline = (self.check_date + relativedelta(days=5)).strftime('%Y-%m-%d')

    @api.multi
    def action_done(self):
        self.labor_id.after_medical_check = self.medical_check
        if self.reason:
           self.labor_id.reason = self.reason
        if self.medical_check == 'fit' and self.labor_id.interpol_no and self.labor_id.specify_agency == 'selected':
            agency = self.env['specify.agent'].search([('labor_id', '=', self.labor_id.id)])
            self.env['labor.embassy'].create({
                'labor_id': self.labor_id.id,
                'passport_no': self.labor_id.passport_no,
                'interpol_no': self.labor_id.interpol_no,
                'big_medical': 'fit',
                'agency': agency.agency.id,
                'employer': agency.employer,
                'city': agency.destination_city,
                'visa_no': agency.visa_no,
            })
            self.env['labor.clearance'].create({
                'labor_id': self.labor_id.id,
                'passport_no': self.labor_id.passport_no,
                'gender': self.labor_id.gender,
                'job_title': self.labor_id.occupation,
                'name': self.labor_id.name,
                'contact': self.labor_id.phone,
                'lc1': self.labor_id.lc1.id,
                'lc2': self.labor_id.lc2.id,
                'lc3': self.labor_id.lc3.id,
                'district': self.labor_id.district.id,
                'agency': agency.agency.id,
            })
            self.env['travel.company'].create({
                'labor_id': self.labor_id.id,
                'passport_no': self.labor_id.passport_no,
                'agency': agency.agency.id,
                'agency_code': agency.name,
            })
        self.state='done'

    @api.multi
    def move_gcc(self):
        invoice_line = []
        purchase_journal = self.env['account.journal'].search([('type', '=', 'purchase')])[0]
        accounts = self.product.product_tmpl_id.get_product_accounts()

        invoice_line.append((0, 0, {
            'product_id': self.product.id,
            'name': 'gcc',
            'uom_id': self.product.uom_id.id,
            'price_unit': self.product.list_price,
            'discount': 0.0,
            'quantity': 1,
            'account_id': accounts.get('stock_input') and accounts['stock_input'].id or \
                          accounts['expense'].id,
        }))

        cr = self.env['account.invoice'].create({
            'partner_id': self.gcc.id,
            'state': 'draft',
            'type': 'in_invoice',
            'origin': self.name,
            'journal_id': purchase_journal.id,
            'account_id': self.gcc.property_account_payable_id.id,
            'invoice_line_ids': invoice_line,

        })
        cr.action_invoice_open()
        self.state = 'gcc'

        return {
            'name': _('GCC Invoice'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'domain': [('origin', '=', self.name)]

        }

    @api.multi
    def invoice_hospital(self):
        invoice_line = []
        purchase_journal = self.env['account.journal'].search([('type', '=', 'purchase')])[0]
        accounts = self.product_hospital.product_tmpl_id.get_product_accounts()
        invoice_line.append((0, 0, {
            'product_id': self.product_hospital.id,
            'name': 'Hospital',
            'uom_id': self.product_hospital.uom_id.id,
            'price_unit': self.hospital.cost,
            'discount': 0.0,
            'quantity': 1,
            'account_id': accounts.get('stock_input') and accounts['stock_input'].id or \
                          accounts['expense'].id,
        }))

        cr = self.env['account.invoice'].create({
            'partner_id': self.hospital.id,
            'state': 'draft',
            'type': 'in_invoice',
            'origin': self.name,
            'journal_id': purchase_journal.id,
            'account_id': self.hospital.property_account_payable_id.id,
            'invoice_line_ids': invoice_line,

        })
        cr.action_invoice_open()
        self.state = 'hospital'
        return {
            'name': _('Hospital Invoice'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'domain': [('origin', '=', self.name)]

        }

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('big.medical')
        return super(BigMedical, self).create(vals)


