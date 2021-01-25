from odoo import api, fields, models


class CompanyTaxInfo(models.Model):
    _inherit= "res.company"

    tax_file = fields.Char()
    tax_reg = fields.Char()
    commercial_reg = fields.Char()


class BankAccountSwitchCode(models.Model):
    _inherit= "res.partner.bank"

    swift_code = fields.Char()