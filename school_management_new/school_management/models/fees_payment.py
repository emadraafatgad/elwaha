from odoo import fields, api, models, _
from odoo.exceptions import ValidationError, Warning
from odoo.exceptions import AccessError, UserError


class FeesPaymentStructure(models.Model):
    _name = 'fees.payment.structure'

    fees_type = fields.Many2one('fees.type',required=True)
    amount = fields.Monetary(string='Amount', currency_field='currency_id', store=True)
    intervals = fields.Integer()
    sequence_discount = fields.Float('Discount %')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id, readonly=True)
    fees_payment_id = fields.Many2one('fees.payment')


class FeesPaymentToInvoice(models.Model):
    _name = 'fees.payment.to.invoice'

    fees_type = fields.Many2one('fees.type',required=True)
    amount = fields.Monetary(string='Amount',compute="calculate_total_amount",store=True, currency_field='currency_id')
    sequence_discount = fields.Float('Discount %')
    before_discount_amount = fields.Monetary(string='Before Discount Amount', currency_field='currency_id')
    due_date = fields.Date()
    # intervals = fields.Integer(related='fees_type.max_intervals',store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id, readonly=True)
    fees_payment_id = fields.Many2one('fees.payment')
    installments = fields.Selection([(1,'First Installment'),(2,'Second Installments'),(3,'Third Installments'),
                                     (4,'Forth Installments'),(5,'Fifth Installments')])
    installments_id = fields.Many2one('installment.count', required=True)
    state = fields.Selection([('draft','Draft'),('confirm','Confirmed'),('Send','Send To Invoice')],readonly=True,
                             default='draft')
    tax_ids = fields.Many2many('account.tax')

    @api.depends('sequence_discount')
    def calculate_total_amount(self):
        for rec in self:
            rec.amount = rec.before_discount_amount*(1-rec.sequence_discount/100)

    @api.multi
    def _default_account(self):
        # journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)

        if not self.fees_type.product_id.property_account_income_id.id:
            account = self.fees_type.product_id.categ_id.property_account_income_categ_id.id
        else:
            account = self.fees_type.product_id.property_account_income_id.id
        return account

    @api.multi
    def send_to_invoice(self):
        print("Send Invoice")
        student = self.fees_payment_id.student_id.partner_id
        invoice_obj = self.env["account.invoice"]
        invoice_line_obj = self.env["account.invoice.line"]
        inv_ids = []
        # for acc in self:
        #     # Create Invoice
        student_draft_invoice = invoice_obj.search([('partner_id','=',student.id),('state','=','draft')],limit=1)
        if student:
            if not student_draft_invoice:
                curr_invoice = {
                    'partner_id': student.id,
                    'account_id': student.property_account_receivable_id.id,
                    'state': 'draft',
                    'type': 'out_invoice',
                    'date_invoice': fields.Date.context_today(self),
                    'origin': "Payment # : " +self.fees_payment_id.name,
                    }
                print('curr_invoice',curr_invoice)
                inv_ids = invoice_obj.create(curr_invoice)

            elif student_draft_invoice:
                inv_ids = student_draft_invoice

            if inv_ids:
                prd_account_id = self._default_account()
                # Create Invoice line
                curr_invoice_line = {
                    'product_id':self.fees_type.product_id.id,
                    'name': self.fees_type.payment_type.name,
                    'price_unit': self.amount,
                    'quantity': 1,
                    'invoice_line_tax_ids': [(6, 0, self.tax_ids.ids)]  if self.tax_ids else False,
                    'account_id': prd_account_id,
                    'invoice_id': inv_ids.id,
                }
                print(curr_invoice_line,"curr_invoice_line")
                inv_line_ids = invoice_line_obj.create(curr_invoice_line)
            inv_ids.compute_taxes()
        self.state = 'Send'
        self.fees_payment_id.get_invoice_state()


class FeesAddtionalPayments(models.Model):
    _name = 'fees.payment.input'

    name = fields.Char(string="Description", required=True)
    product_id = fields.Many2one('product.product', string="Related Product")
    fees_type = fields.Many2one('fees.type')
    amount= fields.Monetary(string='Amount', currency_field='currency_id', required=True, store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id, readonly=True)
    payment_id = fields.Many2one('fees.payment')
    state = fields.Selection([('draft', 'Draft'),('confirm','Confirmed'), ('Send', 'Send To Invoice')], default='draft',readonly=True)
    installments = fields.Selection([(1, 'First Installment'), (2, 'Second Installments'), (3, 'Third Installments'),
                                     (4, 'Forth Installments'), (5, 'Fifth Installments')])
    installments_id = fields.Many2one('installment.count', required=True)
    tax_ids = fields.Many2many('account.tax')

    @api.onchange('product_id')
    def product_name_chanage(self):
        if self.product_id:
            self.name = self.product_id.description if self.product_id.description else self.product_id.name

    @api.onchange('fees_type',)
    def fees_type_amount(self):
        if self.fees_type:
            self.amount = self.fees_type.amount
            self.name = self.fees_type.name

    @api.multi
    def _default_account(self):
        if not self.product_id.property_account_income_id.id:
            account = self.product_id.categ_id.property_account_income_categ_id.id
        else:
            account = self.product_id.property_account_income_id.id
        return account

    @api.multi
    def send_input_to_invoice(self):
        print("Send Invoice")
        student = self.payment_id.student_id.partner_id
        invoice_obj = self.env["account.invoice"]
        invoice_line_obj = self.env["account.invoice.line"]
        inv_ids = []
        student_draft_invoice = invoice_obj.search([('partner_id', '=', student.id), ('state', '=', 'draft')], limit=1)
        if student:
            if not student_draft_invoice:
                curr_invoice = {
                    'partner_id': student.id,
                    'account_id': student.property_account_receivable_id.id,
                    'state': 'draft',
                    'type': 'out_invoice',
                    ''
                    'date_invoice': fields.Date.context_today(self),
                    'origin': "Payment # : " + self.payment_id.name,
                }
                print(curr_invoice," curr_invoice ")
                inv_ids = invoice_obj.create(curr_invoice)

            elif student_draft_invoice:
                inv_ids = student_draft_invoice

            if inv_ids:
                prd_account_id = self._default_account()
                # Create Invoice line
                curr_invoice_line = {
                    'name': self.name,
                    'product_id':self.product_id.id,
                    'price_unit': -1*self.amount,
                    'quantity': 1,
                    'invoice_line_tax_ids': [(6, 0, self.tax_ids.ids)] if self.tax_ids else False,
                    'account_id': prd_account_id,
                    'invoice_id': inv_ids.id,
                }
                print("curr_invoice_line")
                inv_line_ids = invoice_line_obj.create(curr_invoice_line)
            inv_ids.compute_taxes()
        self.state = 'Send'
        self.payment_id.get_invoice_state()


class FeesPayment(models.Model):
    _name = 'fees.payment'

    name = fields.Char(string="Code" )
    student_id = fields.Many2one('student.student', required=True)
    student_sequence_id = fields.Many2one('student.sequence',compute='get_student_data',store=True)
    education_stage = fields.Many2one('education.stage', related='student_id.education_stage',store=True)
    stage_level = fields.Many2one('education.stage.year', related='student_id.stage_level',store=True)
    # fees_structure = fields.Many2one('fees.rules.structure', required=True, readonly=True,states={'draft': [('readonly', False)]})
    fees_structure_line = fields.One2many('fees.payment.structure', 'fees_payment_id',)
    fees_to_invoice = fields.One2many('fees.payment.to.invoice', 'fees_payment_id',)
    payment_input = fields.One2many('fees.payment.input', 'payment_id' )
    one_time_installment = fields.Boolean(readonly=True,states={'draft': [('readonly', False)]})
    invoice_installment = fields.Integer(default=1,string="Next Installment", readonly=True)
    installments_id = fields.Many2one('installment.count', required=False,readonly=True, default=lambda self: self.env['installment.count'].search([('number', '=', 1)],limit=1))
    state = fields.Selection([('draft','Draft'),('confirm','Confirmed'),('Invoice','To Invoice'),
                              ("invoiced","Fully Invoiced",)],default="draft")
    invoice_state = fields.Selection([('not','Not Invoiced'),('partially','Partially Invoiced'),
                                      ('fully','Fully Invoiced')],compute='get_invoice_state',store=False,default='not')
    total_amount =  fields.Monetary(string='Total Amount', currency_field='currency_id', compute='calculate_total_amount' , store=True)
    invoiced_amount = fields.Monetary(string='Invoiced Amount', currency_field='currency_id',
                                   compute='calculate_total_amount', store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id, readonly=True)

    @api.depends('fees_to_invoice.amount','fees_to_invoice.state')
    def calculate_total_amount(self):
        for payment in self:
            total= 0.0
            invoiced = 0.0
            for line in payment.fees_structure_line:
                total += line.amount
            for line in payment.fees_to_invoice:
                if line.state == 'Send':
                    invoiced += line.amount
            payment.update({
                'total_amount': total,
                'invoiced_amount':invoiced,
            })

    @api.depends('fees_to_invoice.state')
    def get_invoice_state(self):
        for rec in self:
            total_count = 0
            total_draft = 0
            total_send = 0
            states = 'not'
            for line in rec.fees_to_invoice:
                if line.state == 'Send':
                    total_send = total_send + 1
                    total_count = total_count + 1
                elif line.state == 'confirm':
                    total_draft = total_draft + 1
                    total_count = total_count + 1
            print(total_count,total_send,total_draft,"Totals Draft")
            if total_send == total_count and total_count != 0:
                rec.invoice_state = 'fully'
                print(rec.invoice_state,rec.state)
                rec.update({'state':'invoiced'})
                print(rec.invoice_state,rec.state,"================")
            elif total_draft > 0 and total_send >1:
                rec.invoice_state = 'partially'
            elif total_draft == total_count:
                rec.invoice_state = 'not'

    @api.depends('student_id')
    def get_student_data(self):
        for rec in self:
            print("i am in Student",rec.student_id.student_sequence_id.name)
            rec.student_sequence_id = rec.student_id.student_sequence_id
            # rec.student_sequence = rec.student_id.student_sequence

    @api.multi
    def compute_fees_structure(self):
        structure_payment = self.env['fees.payment.structure']
        self.fees_structure_line = [(5, 0, 0)]
        for line in self.student_id.fees_type:
            print(('student_sequence','=',self.student_id.student_sequence),
                  ('student_sequence_id','=',self.student_id.student_sequence_id.name),
                  "====",'academic_year','=',self.student_id.year.name
                  ,"=====",('stage_level','=',self.student_id.stage_level.name),
                  'fees_type','=',line.payment_type)
            # fees_type = self.env['fees.type'].search([('payment_type','=',line.id),
            #                                           ('education_stage_year','=', self.student_id.stage_level.id)],limit=1)
            discount_rule = self.env['fees.rules.line'].search([('student_sequence_id','=',self.student_id.student_sequence_id.id),
                                                                ('academic_year','=',self.student_id.year.id),
                                                                ('stage_level','=',self.student_id.stage_level.id),
                                                                ('fees_type','=',line.id)])
            print("=========================================================================================")
            print(('student_sequence_id','=',self.student_id.student_sequence_id.id),
                                                                ('academic_year','=',self.student_id.year.id),
                                                                ('stage_level','=',self.student_id.stage_level.id),
                                                                ('fees_type','=',line.id))
            if discount_rule:
                for record in discount_rule:
                    print(discount_rule, "discount_rule")
                    print(line.name, 'amount  ', record.total_amount, 'fees_payment_id  ', self.id)
                    structure_payment.create({'fees_type': line.id, 'amount': record.total_amount,
                                              'sequence_discount':record.discount,
                                              'fees_payment_id': self.id,
                                              })

            elif not discount_rule:
                fees_type = self.env['fees.type'].search([('payment_type','=',line.id)],limit=1)
                if not fees_type:
                    raise Warning(_("THere is no Fees Amount For This Payment Type"))
                else:
                    structure_payment.create({'fees_type': fees_type.id, 'amount': fees_type.amount,
                                              'fees_payment_id': self.id,
                                              })
        self.create_to_invoice_line()
        self.installments_id = self.env['installment.count'].search([('number', '=', 1)],limit=1)
        # self.state = "Computed"

    @api.constrains('fees_to_invoice.amount')
    def check_installment_amount(self):
        for payment in self:
            for line in payment.fees_structure_line:
                print(line.amount,line.fees_type)
                amount_sum = 0
                for rec in payment.fees_to_invoice:
                    print(rec.fees_type,line.fees_type,"=========")
                    if line.fees_type == rec.fees_type:
                        print(amount_sum,rec.amount,"before")
                        amount_sum = rec.amount +amount_sum
                        print(amount_sum, rec.amount,"after")
                print(line.amount,round(amount_sum),"Total")
                if not round(amount_sum)== line.amount:
                    raise UserError(_("Installments Amount TO equal To Tha Basic"))


    @api.multi
    def create_to_invoice_line(self):
        print("To Create Invoie")
        to_invoice_obj = self.env['fees.payment.to.invoice']
        self.fees_to_invoice = [(5,0,0)]
        for line in self.fees_structure_line:
            for payment_installment in line.fees_type.installment_ids:
                payment = payment_installment.amount_after_percentage
                vals={
                    'fees_type': line.fees_type.id,
                    'before_discount_amount': payment,
                    'sequence_discount':line.sequence_discount,
                    'tax_ids':[(6, 0, self.student_id.nationality_id.tax.ids )]  if self.student_id.nationality_id.tax else False,
                    'installments_id': payment_installment.installments.id,
                    'due_date':payment_installment.installment_date,
                    'fees_payment_id': self.id,
                }
                print(vals)
                to_invoice_obj.create(vals)

    @api.multi
    def action_invoice_create(self, ):
        for order in self:
            for line in order.fees_to_invoice:
                if line.installments_id == order.installments_id and line.state == "confirm":
                    line.send_to_invoice()
            for input in order.payment_input  :
                if input.installments_id == order.installments_id and input.state=="confirm":
                    input.send_input_to_invoice()
            order.get_invoice_state()
            if order.invoice_state == 'fully':
                # order.state='invoiced'
                order.installments_id = False
            else:
                next_installment = self.env['installment.count'].search([('number','=',order.invoice_installment +1)])
                print(next_installment,order.invoice_installment)
                order.installments_id = next_installment
                order.invoice_installment = order.invoice_installment+1

    @api.multi
    def confirm_state(self):
        if self.fees_structure_line is not False:
            for line in self.fees_to_invoice:
                line.state = 'confirm'
            for rec in self.payment_input:
                rec.state = 'confirm'
            self.state = 'confirm'
        else:
            raise ValidationError(_("Please Compute This Payment First"))
            # self.compute_fees_structure()

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('fees.payment') or '/'
        return super(FeesPayment, self).create(vals)
