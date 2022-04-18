from odoo import models, fields, api, exceptions, _

class AccountMovesBulxModify(models.Model):
    _inherit = 'account.move'

    total_credit=fields.Float(compute='compute_total_credit_debit')
    total_debit=fields.Float(compute='compute_total_credit_debit')

    @api.multi
    @api.depends('line_ids')
    def compute_total_credit_debit(self):
        for line in self.line_ids:
            self.total_credit += line.credit
            self.total_debit += line.debit




class AccountMovesLineBulxModify(models.Model):
    _inherit = 'account.move.line'

    name = fields.Char(string="بيان")



class AccountJournalBulxModify(models.Model):
    _inherit = 'account.journal'

    _sql_constraints = [
        (
            'unique_short_code',
            'unique (code)',
            'The short code must be unique',
        )
    ]


