from odoo import fields, api, models ,_


class ClinicPormotion(models.Model):
    _name = "oeh.medical.promotion"

    name = fields.Char()
    start_date = fields.Date()
    end_date = fields.Date()
