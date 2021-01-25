from odoo import fields, api, models, _


class SpecialDiscount(models.Model):
    _name = 'special.discount'

    product_id = fields.Many2one('product.product')
    name = fields.Char('Description',required=True)
    product_qty= fields.Integer(required=True,default=1)
    price_unit = fields.Float(required=True)
    price_subtotal = fields.Monetary(string='Discount', store=True, readonly=True, currency_field='currency_id', compute='_compute_amount',
                                      track_visibility='always')
    invoice_id = fields.Many2one('account.invoice')
    currency_id = fields.Many2one('res.currency')

    @api.depends('product_qty', 'price_unit')
    def _compute_amount(self):
        for line in self:
            # taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_subtotal': line.product_qty * line.price_unit
            })


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    advanced_payment = fields.Float()
    special_discount = fields.One2many('special.discount','invoice_id')
    bl_no = fields.Char()
    ship_date = fields.Date()
    ship_via = fields.Char()
    pol = fields.Many2one('container.port', string='Port Of Loading')
    pod = fields.Many2one('container.port', string='Port Of Discharge')
    vessel_voyage_no = fields.Char(string='Vessel & Voyage No')

    @api.multi
    def action_invoice_open(self):
        origin = self.env['operation.order'].search([('name', '=', self.origin)])
        for org in origin:
            org.invoice_id = self.id
        return super(AccountInvoice , self).action_invoice_open()

    # @api.one
    # @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
    #              'currency_id', 'company_id', 'date_invoice', 'type')
    # def compute_discount(self):
    #     round_curr = self.currency_id.round
    #     self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
    #     self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
    #     self.amount_total = self.amount_untaxed + self.amount_tax
    #     discount = 0
    #     for line in self.invoice_line_ids:
    #         discount += (line.price_unit * line.quantity * line.discount) / 100
    #     self.discount = discount
    #     amount_total_company_signed = self.amount_total
    #     amount_untaxed_signed = self.amount_untaxed
    #     if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
    #         currency_id = self.currency_id.with_context(date=self.date_invoice)
    #         amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
    #         amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
    #     sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
    #     self.amount_total_company_signed = amount_total_company_signed * sign
    #     self.amount_total_signed = self.amount_total * sign
    #     self.amount_untaxed_signed = amount_untaxed_signed * sign
    #
    #
