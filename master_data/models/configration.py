from odoo import fields, models


class ProductConfig(models.Model):
    _name = 'product.recruitment.config'
    _description = 'Product Config'
    _rec_name = 'product'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        ('type_uniq', 'unique (type)', 'Type is already exist')
    ]

    product = fields.Many2one('product.product')
    price = fields.Float()
    type = fields.Selection([('nira', 'Nira'),('passport', 'Passport Broker'),('passport_placing_issue', 'Passport Placing Issue'), ('interpol', 'Interpol Broker'),('gcc', 'GCC'),('hospital', 'Hospital'),('agency', 'Agency'),('training', 'Training')], string='Type',required=True)
