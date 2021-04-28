from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError, AccessError


# class PaymentType(models.Model):
#     _name = 'fees.payment.type'
#
#     name = fields.Char(required=True)
#     max_intervals = fields.Integer(string="Installments",)

    # @api.constrains('max_intervals')
    # def max_intervals_const(self):
    #     for rec in self:
    #         if not rec.max_intervals>0:
    #             raise ValidationError(_('You cannot create Payment With Zero(0) Intervals.'))


class InstallmentCount(models.Model):
    _name = 'installment.count'

    name = fields.Char(required=True)
    number = fields.Integer(readonly=False)

    @api.model
    def create(self, vals):
        vals['number'] = self.env['ir.sequence'].next_by_code('installment.count')
        return super(InstallmentCount, self).create(vals)

    _sql_constraints = [
        ('number_uniq', 'unique(number)', 'Number must be unique!'),('name_unique', 'unique(name)', 'Name must be unique!')
    ]


class FeesInstallment(models.Model):
    _name = 'fees.installments'

    installments = fields.Many2one('installment.count', required=True)
    installment_date = fields.Date("Installment Date",required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    amount = fields.Monetary(string='Amount', currency_field='currency_id', required=True)
    percentage = fields.Float("Percentage %",required=True)
    amount_after_percentage = fields.Monetary(string='Installment Amount', currency_field='currency_id',
                                              compute="calculate_amount_after_percentage",store=True)
    fees_type_id = fields.Many2one('fees.type')

    @api.depends('percentage')
    def calculate_amount_after_percentage(self):
        for rec in self:
            print(rec.amount,"Amount ",rec.percentage,"Percentage")
            rec.amount_after_percentage = rec.amount*rec.percentage/100

    @api.constrains('percentage')
    def percentage_constrain(self):
        for line in self:
            if line.percentage <= 0:
                raise ValidationError(_("you can't create installment Percentage less or equal zero."))

    @api.constrains('amount_after_percentage')
    def non_zero_amount(self):
        for line in self:
            if line.amount_after_percentage <= 0:
                raise ValidationError(_("you can't create installment amount less or equal zero."))


class FeesType(models.Model):
    _name = 'fees.type'
    # _inherits = {'product.product': 'product_id'}
    _rec_name = 'payment_type'

    product_id = fields.Many2one('product.product', string='Related Product', domain="[('is_fees', '=', True)]",required=True, ondelete='cascade')
    payment_type = fields.Char(required=True)
    name = fields.Char()
    academic_year = fields.Many2one('academic.year')
    education_stage = fields.Many2one('education.stage')
    education_stage_year = fields.Many2one('education.stage.year', string="Stage Level",domain="[('stage_id','=',education_stage)]")
    amount = fields.Monetary(string='Amount', currency_field='currency_id', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    max_intervals = fields.Integer(string="Installments ")
    installment_ids = fields.One2many('fees.installments','fees_type_id')

    # @api.constrains('max_intervals')
    # def max_intervals_const(self):
    #     for rec in self:
    #         if not rec.max_intervals>0:
    #             raise ValidationError(_('You cannot create Payment With Zero(0) Intervals.'))

    @api.constrains('installment_ids')
    def installment_amount_limit(self):
        amount = 0
        for line in self.installment_ids:
            amount = line.amount_after_percentage + amount
            print(amount,"amount amount")
        if amount > self.amount:
            raise ValidationError(_('Total installments Amount must be equal to this fees amount'))
        elif amount < self.amount:
            raise ValidationError(_('Total installments Amount must be equal to this fees amount'))

    # @api.model
    # def create(self, vals):
    #     '''Method to create user when student is created'''
    #     print(vals['payment_type'],"=======")
    #     payment_type = self.env['fees.payment.type'].search([('id','=',vals['payment_type'])])
    #     print(payment_type.name)
    #     vals['name'] = payment_type.name
    #     print(vals['name'])
    #     res = super(FeesType, self).create(vals)
    #     return res