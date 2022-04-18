# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    @api.multi
    def clear_cache(self):
        self.ensure_one()
        self.env['product.index'].search([]).unlink()
        self.env['customer.index'].search([]).unlink()
