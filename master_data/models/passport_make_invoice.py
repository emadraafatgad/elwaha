from odoo import fields, models , api,_
from datetime import date

from odoo.exceptions import ValidationError


class PassportInvoice(models.Model):
    _name = 'passport.request.invoice'
    _description = 'Passport Request Invoice'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Number",readonly=True,default='New')
    placing_issue = fields.Many2one('res.partner',string='Placing Issue',domain=[('supplier','=',True)])
    state = fields.Selection([('new', 'new'),('invoiced', 'Invoiced')], default='new',track_visibility='onchange')
    issued_date = fields.Date(default=date.today(),readonly=True)
    passport_request = fields.Many2many('passport.request', string='Passport Requests')

    def _get_product_default(self):

        product = self.env['product.recruitment.config'].search([('type', '=', 'passport')])
        self.product = product.product

    product = fields.Many2one('product.product',compute=_get_product_default)



    @api.multi
    def action_invoice(self):
        for l in self.passport_request:
            if not l.prn:
                raise ValidationError(_('You must enter prn and invoice No to all list'))
            if not l.invoice_no :
                raise ValidationError(_('You must enter prn and invoice No to all list'))
        desc = ''
        for description in self.passport_request:
            desc += description.prn + ','
        invoice_line = []
        purchase_journal = self.env['account.journal'].search([('type', '=', 'purchase')])[0]
        accounts = self.product.product_tmpl_id.get_product_accounts()
        invoice_line.append((0, 0, {
            'product_id': self.product.id,
            'name': desc,
            'uom_id': self.product.uom_id.id,
            'price_unit': self.placing_issue.cost,
            'discount': 0.0,
            'quantity': float(len(self.passport_request)),
            'account_id': accounts.get('stock_input') and accounts['stock_input'].id or \
                          accounts['expense'].id,
        }))
        cr =self.env['account.invoice'].create({
            'partner_id': self.placing_issue.id,
            'type': 'in_invoice',
            'origin': self.name,
            'journal_id': purchase_journal.id,
            'account_id': self.placing_issue.property_account_payable_id.id,
            'invoice_line_ids': invoice_line,

        })
        cr.action_invoice_open()
        return {
            'name': _('Passport List Invoice'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'domain' :[('origin','=',self.name)]

        }




    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('passport.request.invoice')
        return super(PassportInvoice, self).create(vals)

class PassportAccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    @api.onchange('number')
    def action_invoice_open(self):
        origin = self.env['passport.request.invoice'].search([('name', '=', self.origin)])
        for org in origin:
            org.state = 'invoiced'
            org.invoice_date = date.today()
        for list in origin.passport_request:
            list.pass_from = self.partner_id.name
            list.state = 'invoiced'
            list.invoice_id = self.id
            list.invoice_date = date.today()
        return super(PassportAccountInvoice, self).action_invoice_open()