from odoo import fields, api, models


class StudentFeesLine(models.Model):
    _name = 'fees.rules.line'

    student_sequence = fields.Selection([(1, 'The First'), (2, 'The Second'),
                                         (3, 'The Third'), (4, 'The Fourth')])
    student_sequence_id = fields.Many2one('student.sequence', required=True)
    total_amount = fields.Monetary(string='Total Amount', compute='calc_total_amount', store=True,
                                   currency_field='currency_id')
    amount = fields.Monetary(string='Amount', currency_field='currency_id',
                             compute='get_amount_for_stage_year', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id, readonly=True)
    academic_year = fields.Many2one('academic.year')
    discount = fields.Integer('Discount %')
    fees_type = fields.Many2one('fees.type', required=True, domain="[('education_stage_year','=',stage_level)]")
    stage_level = fields.Many2one('education.stage.year')
    fees_rule_id = fields.Many2one('fees.rules')

    @api.depends('fees_type')
    def get_amount_for_stage_year(self):
        for rec in self:
            rec.amount = rec.fees_type.amount

    @api.depends('amount', 'discount')
    def calc_total_amount(self):
        for rec in self:
            if rec.amount:
                rec.total_amount = rec.amount * (100 - rec.discount) / 100
                print(rec.total_amount)


class StudentFees(models.Model):
    _name = 'fees.rules'

    name = fields.Char(required=True)
    academic_year = fields.Many2one('academic.year', required=True)
    education_stage = fields.Many2one('education.stage')
    stage_level = fields.Many2one('education.stage.year', domain="[('stage_id','=',education_stage)]")
    discount = fields.Integer('Discount %', required=True)
    student_sequence = fields.Selection([(1, 'The First'), (2, 'The Second'),
                                         (3, 'The Third'), (4, 'The Fourth')], )
    student_sequence_id = fields.Many2one('student.sequence', required=True)
    rules_line_ids = fields.One2many('fees.rules.line', 'fees_rule_id')

    @api.multi
    def generate_rules_line(self):
        stages_year = self.env['education.stage.year'].search([])
        fees_rule = self.env['fees.rules.line']
        print(stages_year, "stage year")
        # self.rules_line_ids = [(5, 0, 0)]
        for stage in stages_year:
            print(stage, "stage ")
            payment_type = self.env['fees.type'].search([('education_stage_year', '=', stage.id)])
            print(payment_type, "payment_type year")
            for payment in payment_type:
                print(payment_type, "payment_type")
                vals = {
                    'student_sequence_id': self.student_sequence_id.id,
                    'academic_year': self.academic_year.id,
                    'stage_level': stage.id,
                    'discount': self.discount,
                    'fees_type': payment.id,
                    'fees_rule_id': self.id}
                print(vals)
                fees_rule.create(vals)
        rules_list = self.env['fees.rules.line'].search_read([('fees_rule_id', '=', self.id)])
        return {'message': 'Rules Generate success.', 'rules_list': rules_list}


class StudentFeesStructure(models.Model):
    _name = 'fees.rules.structure'

    name = fields.Char(required=True)
    academic_year = fields.Many2one('academic.year')
    # education_stage = fields.Many2one('education.stage')
    # stage_level = fields.Many2one('education.stage.year', domain="[('stage_id','=',education_stage)]")
    # student_sequence = fields.Selection([(1, 'The First'), (2, 'The Second'), (3, 'The Third'), (4, 'The Fourth')],
    #                                     required=False)
    # student_sequence_id = fields.Many2one('student.sequence',required=False)
    # rules_line_ids = fields.Many2many('fees.payment.type')
