from odoo import fields, models , api,_
from datetime import date

from odoo.exceptions import ValidationError


class NiraLetter(models.Model):
    _name = 'nira.letter.request'
    _description = 'Nira Letter Request'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    sequence = fields.Char('Sequence',default="New",size=256,readonly=True)
    labourer_id = fields.Many2one('labor.profile',readonly=True)
    name = fields.Char(string="Name",readonly=True)
    code = fields.Char(string="Code")
    reject_reason = fields.Char()
    birth_date = fields.Date(string="Date Of Birth",readonly=True)
    request_date = fields.Date("Request Date",readonly=True)
    invoice_date = fields.Date("Invoice Date")
    delivery_date = fields.Date("Delivery Date")
    start_date = fields.Date('Issued Date')
    end_date = fields.Date("Expired Date")
    state = fields.Selection([('new', 'New'), ('releasing', 'Releasing'),('done', 'Done'),('rejected', 'Rejected')], default='new',track_visibility="onchange")
    national_id = fields.Char('National ID',size=14)
    broker_list_id = fields.Many2one('nira.broker')
    broker = fields.Many2one('res.partner')

    def _get_product_default(self):
        product = self.env['product.recruitment.config'].search([('type', '=', 'nira')])
        for rec in self:
            rec.product = product.product

    product = fields.Many2one('product.product', compute=_get_product_default)

    @api.onchange('national_id')
    def onchange_national_id(self):
        if self.national_id:
            if len(self.national_id) < 14:
                message = _(('ID must be 14!'))
                mess = {
                    'title': _('Warning'),
                    'message': message
                }
                return {'warning': mess}

    @api.multi
    def nira_request_approve(self):
        self.invoice_date = date.today()
        return self.write({'state': 'invoiced'})

    @api.multi
    def nira_request_done(self):
        for rec in self:
            if not rec.national_id or not rec.start_date:
                raise ValidationError(_('Enter nira info'))
            rec.labourer_id.national_id = rec.national_id
            rec.labourer_id.start_date = rec.start_date
            rec.labourer_id.end_date = rec.end_date
            rec.state = 'done'
            invoice_line = []
            purchase_journal = self.env['account.journal'].search([('type', '=', 'purchase')])[0]
            accounts = self.product.product_tmpl_id.get_product_accounts()
            invoice_line.append((0, 0, {
                'product_id': rec.product.id,
                'name': rec.labourer_id.name,
                'uom_id': rec.product.uom_id.id,
                'price_unit': rec.broker.cost,
                'discount': 0.0,
                'quantity': 1,
                'account_id': accounts.get('stock_input') and accounts['stock_input'].id or \
                              accounts['expense'].id,
            }))
            invoice = self.env['account.invoice'].search(
                [('origin', '=', self.broker_list_id.name), ('state', '=', 'draft'),('type', '=', 'in_invoice')])
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





    @api.multi
    def nira_reject(self):
        for rec in self:
            if not rec.reject_reason:
                raise ValidationError(_('Enter any reject reason'))
            rec.state = 'rejected'
            invoice_line = []
            purchase_journal = self.env['account.journal'].search([('type', '=', 'purchase')])[0]
            accounts = self.product.product_tmpl_id.get_product_accounts()
            invoice_line.append((0, 0, {
                'product_id': rec.product.id,
                'name': rec.labourer_id.name,
                'uom_id': rec.product.uom_id.id,
                'price_unit': rec.broker.cost,
                'discount': 0.0,
                'quantity': 1,
                'account_id': accounts.get('stock_input') and accounts['stock_input'].id or \
                              accounts['expense'].id,
            }))
            invoice = self.env['account.invoice'].search(
                [('origin', '=', self.broker_list_id.name), ('state', '=', 'draft'),('type', '=', 'in_refund')])
            if invoice:
                invoice.write({'invoice_line_ids': invoice_line})
            else:
                self.env['account.invoice'].create({
                    'partner_id': rec.broker.id,
                    'type': 'in_refund',
                    'origin': rec.broker_list_id.name,
                    'journal_id': purchase_journal.id,
                    'account_id': rec.broker.property_account_payable_id.id,
                    'invoice_line_ids': invoice_line,

                })


    @api.model
    def create(self, vals):
        vals['sequence'] = self.env['ir.sequence'].next_by_code('nira.letter.request')
        vals['request_date'] = date.today()
        return super(NiraLetter, self).create(vals)



