# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountDiscount(models.Model):
    _inherit = 'account.invoice'

    discount_lines= fields.One2many(
        comodel_name='discount.line',
        inverse_name='invoice_id',
        string='Discount Lines',
        required=False)

    ks_amount_discount = fields.Monetary(string='Discount', readonly=True, compute='_compute_amount',
                                         store=True, track_visibility='always')

    def _compute_amount(self):
        for rec in self:
            res = super(AccountDiscount, rec)._compute_amount()
            rec.ks_calculate_discount()
        return res

    @api.multi
    def ks_calculate_discount(self):
        for rec in self:
            discount_sum = 0.0
            for line in rec.discount_lines:
                discount_sum += line.amount
            rec.ks_amount_discount = discount_sum
            rec.amount_total = rec.amount_tax + rec.amount_untaxed - rec.ks_amount_discount

    @api.model
    def invoice_line_move_line_get(self):
        ks_res = super(AccountDiscount, self).invoice_line_move_line_get()
        if self.ks_amount_discount > 0 and self.ks_amount_discount  < self.amount_total:
            for rec in self.discount_lines:
                dict = {
                        'invl_id': self.number,
                        'type': 'src',
                        'name': rec.name,
                        'price_unit': rec.amount,
                        'quantity': 1,
                        'price': -rec.amount,
                        'account_id': rec.account_id.id,
                        'invoice_id': self.id,
                    }
                ks_res.append(dict)
        return ks_res


class discount_line(models.Model):
    _name = 'discount.line'
    name=fields.Char(
        string='Description',required=True,
    )
    account_id=fields.Many2one(
        comodel_name='account.account',
        string='Account',
        required=True)

    amount=fields.Float(
        string='Amount',
        required=True)

    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Invoice',
        required=False)



