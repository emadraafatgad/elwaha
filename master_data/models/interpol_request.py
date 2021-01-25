from odoo import fields, models , api,_
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class InterpolRequest(models.Model):
    _name = 'interpol.request'
    _description = 'Interpol Request'
    _rec_name = 'labor_id'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Number",readonly=True,default='New')
    labor_id = fields.Many2one('labor.profile')
    labor = fields.Char('Labor Name')
    request_date = fields.Datetime(readonly=True, index=True, default=fields.Datetime.now)
    end_date = fields.Date('Delivery Date')
    broker = fields.Many2one('res.partner')
    national_id = fields.Char('National ID',size=14,required=True)
    state = fields.Selection([('new','New'),('assigned','Assigned'),('rejected','rejected'),
                             ('done','Done')],default='new',track_visibility="onchange")

    passport_no = fields.Char()
    interpol_no = fields.Char('Interpol No')
    attachment = fields.Binary()
    filename  = fields.Char()
    interpol_start_date = fields.Date('Interpol Start Date')
    interpol_end_date = fields.Date('Interpol End Date')
    note = fields.Text()
    broker_list_id = fields.Many2one('interpol.broker')

    @api.onchange('interpol_start_date')
    def onchange_interpol_date(self):
        if self.interpol_start_date:
            self.interpol_end_date = (self.interpol_start_date + relativedelta(months=6)).strftime('%Y-%m-%d')

    def _get_product_default(self):
        product = self.env['product.recruitment.config'].search([('type', '=', 'interpol')])
        for rec in self:
            rec.product = product.product

    product = fields.Many2one('product.product', compute=_get_product_default)

    @api.multi
    def interpol_invoice(self):
        self.invoice_date = date.today()
        self.state = 'invoiced'

    @api.multi
    def interpol_request_done(self):
        agency = self.env['specify.agent'].search([('labor_id', '=', self.id)])
        for rec in self:
            if not rec.interpol_no or not rec.attachment:
                raise ValidationError(_('You must enter interpol info'))
            else:
                rec.end_date = date.today()
                rec.labor_id.interpol_no = rec.interpol_no
                rec.labor_id.interpol_start_date = rec.interpol_start_date
                rec.labor_id.interpol_end_date = rec.interpol_end_date
                rec.state = 'done'

            if self.labor_id.after_medical_check == 'fit' and agency.state == 'selected':
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

            invoice_line = []
            purchase_journal = self.env['account.journal'].search([('type', '=', 'purchase')])[0]
            accounts = self.product.product_tmpl_id.get_product_accounts()
            invoice_line.append((0, 0, {
                'product_id': rec.product.id,
                'name': rec.labor_id.name,
                'uom_id': rec.product.uom_id.id,
                'price_unit': rec.broker_list_id.broker.cost,
                'discount': 0.0,
                'quantity': 1,
                'account_id': accounts.get('stock_input') and accounts['stock_input'].id or \
                              accounts['expense'].id,
            }))
            invoice = self.env['account.invoice'].search([('origin', '=', self.broker_list_id.name),('state','=','draft')])
            if invoice:
                invoice.write({'invoice_line_ids': invoice_line})
            else:
                self.env['account.invoice'].create({
                    'partner_id': rec.broker.id,
                    'state': 'draft',
                    'type': 'in_invoice',
                    'origin': rec.broker_list_id.name,
                    'journal_id': purchase_journal.id,
                    'account_id': rec.broker.property_account_payable_id.id,
                    'invoice_line_ids': invoice_line,

                })

            return {
                'name': _('Interpol List Invoice'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'domain': [('origin', '=', self.broker_list_id.name)]

            }


    @api.multi
    def action_assign(self):
        self.end_date = date.today()
        self.state = 'assigned'

    @api.multi
    def action_reject(self):
        self.state = 'rejected'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('interpol.request')
        return super(InterpolRequest, self).create(vals)


class LaborProfile(models.Model):
    _inherit = 'labor.profile'

    def request_passport(self):
        print("================================")
        request_obj = self.env['passport.request']
        request_obj.create({
            'name':self.passport_no,
            'labor_id':self.id,
        })