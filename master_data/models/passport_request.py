from odoo import fields, models , api,_
from dateutil.relativedelta import relativedelta
from datetime import datetime,date
from odoo.exceptions import UserError, ValidationError


class PassportNumber(models.Model):
    _name = 'passport.request'
    _rec_name = 'labor_id'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    sequence = fields.Char(string="Sequence", readonly=True,default='New')
    name = fields.Char(string="Labor Name",readonly=True)
    national_id = fields.Char(required=True,size=14,string='National ID')
    labor_id = fields.Many2one('labor.profile',required=True)
    broker = fields.Many2one('res.partner')
    request_date = fields.Datetime(readonly=True, index=True, default=fields.Datetime.now)
    invoice_date = fields.Date('Invoice Date')
    invoice_id = fields.Many2one('account.invoice')
    end_date = fields.Date('Delivery Date')
    deadline = fields.Date('Deadline')
    state = fields.Selection([('new','new'),('invoiced','invoiced'),
                              ('releasing','Releasing'),('done','Done')],default='new',track_visibility="onchange")
    passport_no = fields.Char()
    pass_start_date = fields.Date()
    pass_end_date = fields.Date()
    pass_from = fields.Char()
    prn = fields.Char('PRN NO')
    invoice_no = fields.Char('Invoice Number')
    note = fields.Text()
    filename = fields.Char()
    attachment = fields.Binary()
    seq = fields.Integer()
    row_num = fields.Char()
    broker_list_id = fields.Many2one('passport.broker')
    def _get_product_default(self):
        product = self.env['product.recruitment.config'].search([('type', '=', 'passport')])
        for rec in self:
            rec.product = product.product

    product = fields.Many2one('product.product', compute=_get_product_default)
    @api.multi
    def request_passport_approve(self):
        self.state = 'releasing'
    @api.multi
    def request_passport_done(self):
        for rec in self:
            if not rec.passport_no or not rec.pass_start_date or not rec.pass_end_date or not rec.pass_from:
                raise ValidationError(_('You must enter passport info'))
            else:
                rec.labor_id.passport_no = rec.passport_no
                rec.labor_id.prn = rec.prn
                rec.labor_id.pass_start_date = rec.pass_start_date
                rec.labor_id.pass_end_date = rec.pass_end_date
                rec.labor_id.pass_from = rec.pass_from
                rec.state = 'done'
                rec.labor_id.request_interpol()
                rec.labor_id.big_medical_request()
                rec.labor_id.specify_agency_request()

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
            invoice = self.env['account.invoice'].search([('origin', '=', rec.broker_list_id.name),('state','=','draft')])
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


    @api.onchange('pass_start_date')
    def onchange_pass_date(self):
        if self.pass_start_date:
            self.pass_end_date = (self.pass_start_date + relativedelta(years=10)).strftime('%Y-%m-%d')



    @api.model
    def create(self, vals):
      sequence = self.env['ir.sequence'].next_by_code('passport.release')
      vals['sequence'] = sequence
      return super(PassportNumber, self).create(vals)








