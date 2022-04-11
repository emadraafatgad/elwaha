# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime ,time
from odoo.tools import float_is_zero, float_compare


class JournalEnrty(models.Model):
    _inherit = 'account.move'

    check_rate = fields.Boolean(help='Cantidad de unidades de la moneda base con respecto a la moneda extranjera',
                                string='check rate')
    f_currency_id = fields.Many2one('res.currency', string="Currency")
    rate_exchange = fields.Float(help='Cantidad de unidades de la moneda base con respecto a la moneda extranjera',
                                 string='rate exchange')
    to_amount = fields.Float(string='currency price')
    exchange_amount = fields.Float()

    @api.onchange('exchange_amount', 'rate_exchange')
    def currency_price(self):
        if self.rate_exchange:
            self.to_amount = self.exchange_amount * self.rate_exchange


class JournalItem(models.Model):
    _inherit = 'account.move.line'

    rate_exchange = fields.Float(help='Cantidad de unidades de la moneda base con respecto a la moneda extranjera',
                                 string='rate exchange')

    @api.onchange('amount_currency','rate_exchange', 'currency_id', 'account_id')
    def _onchange_amount_currency(self):
        '''Recompute the debit/credit based on amount_currency/currency_id and date.
        However, date is a related field on account.move. Then, this onchange will not be triggered
        by the form view by changing the date on the account.move.
        To fix this problem, see _onchange_date method on account.move.
        '''
        for line in self:
            company_currency_id = line.account_id.company_id.currency_id
            amount = line.amount_currency
            if line.currency_id and company_currency_id and line.currency_id != company_currency_id and not line.rate_exchange:
                amount = line.currency_id._convert(amount, company_currency_id, line.company_id,
                                                   line.date or fields.Date.today())
                line.debit = amount > 0 and amount or 0.0
                line.credit = amount < 0 and -amount or 0.0
            elif line.currency_id and company_currency_id and line.currency_id != company_currency_id and line.rate_exchange:
                rate = line.rate_exchange
                if rate > 0:
                    amount = amount * rate
                    line.debit = amount > 0 and amount or 0.0
                    line.credit = amount < 0 and -amount or 0.0
                else:
                    amount = line.currency_id._convert(amount, company_currency_id, line.company_id,
                                                       line.date or fields.Date.today())
                    line.debit = amount > 0 and amount or 0.0
                    line.credit = amount < 0 and -amount or 0.0


# class CurrencyRate(models.Model):
#     _inherit = "res.currency.rate"

    # name = fields.DateTime(string='Date', required=True, index=True,
    #                        default=fields.Date.context_today)
    #
    # _sql_constraints = [
    #     ('unique_name_per_day', 'CHECK (1=1)', 'Only one currency rate per day allowed!'),
    #     ('currency_rate_check', 'CHECK (rate>0)', 'The currency rate must be strictly positive.'),
    # ]

    # @api.model
    # def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
    #     if operator in ['=', '!=']:
    #         try:
    #             date_format = '%Y-%m-%d %H:%M'
    #             if self._context.get('lang'):
    #                 lang_id = self.env['res.lang']._search([('code', '=', self._context['lang'])],
    #                                                        access_rights_uid=name_get_uid)
    #                 if lang_id:
    #                     date_format = self.browse(lang_id).date_format
    #             name = time.strftime('%Y-%m-%d %H:%M', time.strptime(name, date_format))
    #         except ValueError:
    #             try:
    #                 args.append(('rate', operator, float(name)))
    #             except ValueError:
    #                 return []
    #             name = ''
    #             operator = 'ilike'
    #     return super(CurrencyRate, self)._name_search(name, args=args, operator=operator, limit=limit,
    #                                                   name_get_uid=name_get_uid)
    #
