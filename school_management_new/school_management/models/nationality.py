# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class Nationality(models.Model):
    _name = 'school.nationality'
    _rec_name = 'name'

    name = fields.Char('Nationality',required=True)
    country_id = fields.Many2one('res.country',required=True)
    tax = fields.Many2many('account.tax')
