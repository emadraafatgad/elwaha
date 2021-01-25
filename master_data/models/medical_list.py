from odoo import fields, models,api,_
from odoo.exceptions import ValidationError


class MedicalList(models.Model):
    _name = 'medical.list'
    _description = 'Medical List'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Number",readonly=True,default='New')
    medical_request = fields.Many2many('big.medical',required=True)
    hospital = fields.Many2one('res.partner', domain=[('vendor_type','=','hospital')])
    state = fields.Selection([('new', 'New'), ('invoiced', 'Invoiced'),('done', 'Done')], default='new', track_visibility="onchange")
    def _get_product_default(self):
        product = self.env['product.recruitment.config'].search([('type', '=', 'hospital')])
        self.product = product.product

    product = fields.Many2one('product.product',compute=_get_product_default)
    @api.multi
    def action_confirm(self):
        for list in self.medical_request:
            if list.medical_check:
               list.action_done()
            else:
                raise ValidationError(_('You must enter medical check information to all list'))
        self.state = 'done'

    @api.multi
    def invoice(self):
        self.state = 'invoiced'
        for rec in self.medical_request:
            invoice_line = []
            purchase_journal = self.env['account.journal'].search([('type', '=', 'purchase')])[0]
            accounts = self.product.product_tmpl_id.get_product_accounts()

            invoice_line.append((0, 0, {
                'product_id': self.product.id,
                'name': 'Hospital',
                'uom_id': self.product.uom_id.id,
                'price_unit': self.product.list_price,
                'discount': 0.0,
                'quantity': 1,
                'account_id': accounts.get('stock_input') and accounts['stock_input'].id or \
                              accounts['expense'].id,
            }))

            cr = self.env['account.invoice'].create({
                'partner_id': rec.hospital.id,
                'state': 'draft',
                'type': 'in_invoice',
                'origin': self.name,
                'journal_id': purchase_journal.id,
                'account_id': rec.hospital.property_account_payable_id.id,
                'invoice_line_ids': invoice_line,

            })
            cr.action_invoice_open()
            rec.state = 'hospital'
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
        vals['name'] = self.env['ir.sequence'].next_by_code('medical.list')
        return super(MedicalList, self).create(vals)




