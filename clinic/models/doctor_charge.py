from odoo import api, fields, models, _


class AmountDrPercentage(models.Model):
    _name = 'amount.dr.percentage'
    _rec_name = 'doctor'

    doctor = fields.Many2one('oeh.medical.physician', string='Doctor', help="Current primary care", domain=[],)

    work_date = fields.Date(default=fields.Date.today)
    amount_total = fields.Float(compute='compute_total_amount_for_doctor',store=True,readonly=False)
    minimum_amount = fields.Float(related='doctor.minimum_charge',store=True)

    @api.depends('doctor','work_date')
    def compute_total_amount_for_doctor(self):
        amount_lines = self.env['amount.dr.percentage.line'].search([('doctor','=',self.doctor.id),('work_date','=',
                                                                                                    self.work_date)])
        total_amount  = 0.0
        for amount_line in amount_lines:
            total_amount += amount_line.amount
            print(total_amount)
        self.amount_total = total_amount

    def check_dr_min_charge(self):
        payment_amount = 0
        if self.amount_total < self.minimum_amount:
            payment_amount = self.minimum_amount
        elif self.amount_total > self.minimum_amount:
            payment_amount = self.amount_total
        print(payment_amount)
        # return payment_amount


class AmountDrPercentageLine(models.Model):
    _name = 'amount.dr.percentage.line'

    doctor = fields.Many2one('oeh.medical.physician', string='Doctor', help="Doctor That want to Calculate his salary",
                             readonly=False)
    service_id = fields.Many2one('oeh.medical.service',string="Session Name")
    work_date = fields.Date()
    amount = fields.Float()


class DoctorPriceListLine(models.Model):
    _name = 'doctor.price.list.line'
    _rec_name = "service_id"

    service_id = fields.Many2one(' ','Session')
    percentage = fields.Float(placeholder='%')


class DoctorPriceList(models.Model):
    _name = 'doctor.price.list'

    name = fields.Char()
    clinic = fields.Many2one('res.company')
    price_list_line = fields.Many2many('doctor.price.list.line')
