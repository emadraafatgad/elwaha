from odoo import models, fields, api, tools, exceptions, _
from odoo.exceptions import ValidationError, UserError


# class account_abstract_paymentBulx(models.AbstractModel):
#     _inherit = "account.abstract.payment"

class PaymentAccountbulxInherit(models.Model):
    _inherit = 'account.payment'

    type = fields.Selection([('vendor_payment', 'Vendor Payment'), ('customer_payment', 'Customer Payment')],
                            string='Type', required=True, readonly=True)
    payment_type = fields.Selection([('outbound', 'Send Money'), ('inbound', 'Receive Money')],
                                    string='Payment Type', required=True)
    destination_journal_id = fields.Many2one('account.journal', string='Transfer To', domain=[('type', '=', 'cash')])
    journal_id = fields.Many2one('account.journal', string='Payment Journal', required=True,
                                 domain=[('type', '=', 'cash')])
    check_number = fields.Char('Check Number')
    with_date = fields.Date('Check Date')
    reason = fields.Char('Description')
    bank = fields.Char(string='Bank')
    branch = fields.Char('Branch')
    bank_select = fields.Char('Reference')
    cus_select = fields.Char('Receipt From')
    destination_account_id = fields.Many2one('account.account', compute='_compute_destination_account_id', readonly=True)
    destination_account_id2 = fields.Many2one('account.account',string='Destination Account',store=True)

    # destination_account_id_expense = fields.Many2one('account.account',string='Destination Account')


    name= fields.Char(string='Sequence', compute='cal_seq_for_treasury', store=True, copy=False)
    short_code = fields.Char(related='journal_id.code', store=True, copy=True)
    second_code = fields.Integer(string='Second Code', compute='cal_seq_for_treasury', store=True, copy=True)
    # name = fields.Char(readonly=True, copy=False)

    @api.multi
    @api.depends('state', 'short_code')
    def cal_seq_for_treasury(self):
        list = []
        for line in self:
            if line.state == 'posted':
                max_seq = self.env['account.payment'].search(
                    [('short_code', '=', line.short_code), ('second_code', '!=', False), ('type', '=', line.type)])
                if max_seq:
                    for rec in max_seq:
                        # mm = rec.name.split('/')
                        # second = int(mm[1])
                        list.append(rec.second_code)

                    counter = (max(list))
                    new = counter + 1
                    line.name = str(line.journal_id.code) + '/' + str(new)
                    line.second_code = new

                else:
                    line.second_code = 1
                    line.name = str(line.journal_id.code) + '/' + str(line.second_code)

    @api.onchange('partner_type', 'partner_id')
    def bank_customer_info(self):
        if self.partner_id and self.partner_type == 'customer':
            self.cus_select = self.partner_id.name

    @api.onchange('destination_account_id')
    def bank_destination_account_info(self):
        if self.destination_account_id.user_type_id.name == 'Bank and Cash':
            self.bank = self.destination_account_id.name

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        if not self.invoice_ids:
            # Set default partner type for the payment type
            if self.type == 'customer_payment':
                if self.payment_type == 'inbound' :
                    self.partner_type = 'customer'
                else:
                    self.partner_type = False
                    raise ValidationError('you can not send money to customer!!')
            elif self.type == 'vendor_payment':
                if self.payment_type == 'outbound' :
                    self.partner_type = 'supplier'
                else:
                    self.partner_type = False
                    raise ValidationError('you can not receive money from vendor!!')
        # Set payment method domain
        res = self._onchange_journal()
        if not res.get('domain', {}):
            res['domain'] = {}
        jrnl_filters = self._compute_journal_domain_and_types()
        journal_types = jrnl_filters['journal_types']
        journal_types.update(['cash'])
        res['domain']['journal_id'] = jrnl_filters['domain'] + [('type', 'in', list(journal_types))]
        return res

    def _compute_journal_domain_and_types(self):
        journal_type = ['cash']
        domain = []
        if self.currency_id.is_zero(self.amount) and hasattr(self, "has_invoices") and self.has_invoices:
            # In case of payment with 0 amount, allow to select a journal of type 'general' like
            # 'Miscellaneous Operations' and set this journal by default.
            journal_type = ['general']
            self.payment_difference_handling = 'reconcile'
        else:
            if self.payment_type == 'inbound':
                domain.append(('at_least_one_inbound', '=', True))
            else:
                domain.append(('at_least_one_outbound', '=', True))
        return {'domain': domain, 'journal_types': set(journal_type)}

    @api.one
    @api.depends('destination_account_id2','invoice_ids', 'payment_type', 'partner_type', 'partner_id')
    def _compute_destination_account_id(self):
        if not self.partner_id:
            self.destination_account_id = self.destination_account_id2.id
        else:
            if self.invoice_ids:
                self.destination_account_id = self.invoice_ids[0].account_id.id
            elif self.payment_type == 'transfer':
                if not self.company_id.transfer_account_id.id:
                    raise UserError(
                        _('There is no Transfer Account defined in the accounting settings. Please define one to be able to confirm this transfer.'))
                self.destination_account_id = self.company_id.transfer_account_id.id
            elif self.partner_id:
                partner = self.partner_id.with_context(force_company=self.company_id.id)
                if self.partner_type == 'customer':
                    self.destination_account_id = partner.property_account_receivable_id.id
                else:
                    self.destination_account_id = partner.property_account_payable_id.id
            elif self.partner_type == 'customer':
                default_account = self.env['ir.property'].with_context(force_company=self.company_id.id).get(
                    'property_account_receivable_id', 'res.partner')
                if default_account:
                 self.destination_account_id = default_account.id
            elif self.partner_type == 'supplier':
                default_account = self.env['ir.property'].with_context(force_company=self.company_id.id).get(
                    'property_account_payable_id', 'res.partner')
                if default_account:
                  self.destination_account_id = default_account.id

    # @api.multi
    # def post(self):
    #     """ Create the journal items for the payment and update the payment's state to 'posted'.
    #         A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
    #         and another in the destination reconcilable account (see _compute_destination_account_id).
    #         If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
    #         If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
    #     """
    #     for rec in self:
    #
    #         if rec.state != 'draft':
    #             raise UserError(_("Only a draft payment can be posted."))
    #
    #         if any(inv.state != 'open' for inv in rec.invoice_ids):
    #             raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
    #
    #         # keep the name in case of a payment reset to draft
    #         if not rec.name:
    #             # Use the right sequence to set the name
    #             if rec.payment_type == 'transfer':
    #                 sequence_code = 'account.payment.transfer'
    #             else:
    #                 if rec.partner_type == 'customer':
    #                     if rec.payment_type == 'inbound':
    #                         sequence_code = 'account.payment.customer.invoice'
    #                     if rec.payment_type == 'outbound':
    #                         sequence_code = 'account.payment.customer.refund'
    #                     else:
    #                         sequence_code = 'account.payment.customer.invoice'
    #                 if rec.partner_type == 'supplier':
    #                     if rec.payment_type == 'inbound':
    #                         sequence_code = 'account.payment.supplier.refund'
    #                     if rec.payment_type == 'outbound':
    #                         sequence_code = 'account.payment.supplier.invoice'
    #                     else:
    #                         sequence_code = 'account.payment.supplier.invoice'
    #             rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(
    #                 sequence_code)
    #             if not rec.name and rec.payment_type != 'transfer':
    #                 raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))
    #
    #         # Create the journal entry
    #         amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
    #         move = rec._create_payment_entry(amount)
    #         persist_move_name = move.name
    #
    #         # In case of a transfer, the first journal entry created debited the source liquidity account and credited
    #         # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
    #         if rec.payment_type == 'transfer':
    #             transfer_credit_aml = move.line_ids.filtered(
    #                 lambda r: r.account_id == rec.company_id.transfer_account_id)
    #             transfer_debit_aml = rec._create_transfer_entry(amount)
    #             (transfer_credit_aml + transfer_debit_aml).reconcile()
    #             persist_move_name += self._get_move_name_transfer_separator() + transfer_debit_aml.move_id.name
    #
    #         rec.write({'state': 'posted', 'move_name': persist_move_name})
    #     return True

    # @api.one
    # @api.depends('partner_type', 'partner_id')
    # def _compute_destination_account_id(self):
    #     # if self.payment_type != 'expense':
    #     #     if self.invoice_ids:
    #     #         self.destination_account_id = self.invoice_ids[0].account_id.id
    #         # elif self.payment_type == 'transfer':
    #         #     if not self.company_id.transfer_account_id.id:
    #         #         raise UserError(
    #         #             _('There is no Transfer Account defined in the accounting settings. Please define one to be able to confirm this transfer.'))
    #         #     self.destination_account_id = self.company_id.transfer_account_id.id
    #         if self.partner_id:
    #             partner = self.partner_id.with_context(force_company=self.company_id.id)
    #             if self.partner_type == 'customer':
    #                 self.destination_account_id = partner.property_account_receivable_id.id
    #             else:
    #                 self.destination_account_id = partner.property_account_payable_id.id
    #         # elif self.partner_type == 'customer':
    #         #     default_account = self.env['ir.property'].with_context(force_company=self.company_id.id).get(
    #         #         'property_account_receivable_id', 'res.partner')
    #         #     if default_account:
    #         #         self.destination_account_id = default_account.id
    #
    #         # elif self.partner_type == 'supplier':
    #         #     default_account = self.env['ir.property'].with_context(force_company=self.company_id.id).get(
    #         #         'property_account_payable_id', 'res.partner')
    #         #     if default_account:
    #         #       self.destination_account_id = default_account.id
    #         # else:
    #         #     self.destination_account_id = False
