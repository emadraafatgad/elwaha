from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging



_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'


    check_rate = fields.Boolean(help='Cantidad de unidades de la moneda base con respecto a la moneda extranjera', string='check rate')
    rate_exchange = fields.Float(help='Cantidad de unidades de la moneda base con respecto a la moneda extranjera', string='rate exchange')
    local_currency_price = fields.Float(string='local currency price')

    @api.onchange('amount', 'rate_exchange')
    def currency_price(self):
        if self.rate_exchange:
            self.local_currency_price = self.amount * self.rate_exchange


class AccountMove(models.Model):
    _inherit = 'account.move.line'


    check_rate = fields.Boolean(help='Cantidad de unidades de la moneda base con respecto a la moneda extranjera', string='check rate')
    rate_exchange = fields.Float(help='Cantidad de unidades de la moneda base con respecto a la moneda extranjera', string='rate exchange')
    local_currency_price = fields.Float(string='local currency price')

    # @api.onchange('amount', 'rate_exchange')
    # def currency_price(self):
    #     if self.rate_exchange:
    #         self.local_currency_price = self.amount / self.rate_exchange

