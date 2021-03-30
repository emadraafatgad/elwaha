from odoo import models, fields, api,_
from odoo.exceptions import ValidationError
from datetime import  date


class PurchasePlan(models.Model):
    _name = 'purchase.plan'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Purchase Plan'

    name = fields.Char(default='New',readonly=True)
    origin = fields.Char(readonly=True,string='Contract Ref')
    # total_qty = fields.Float(required=True)
    # product = fields.Many2many('product.product',required=True)
    purchase_order = fields.Many2many('purchase.order',string='Purchase Orders',readonly=True)
    sent_date = fields.Date(default=date.today(),readonly=True)
    line_ids = fields.One2many('purchase.plan.line','plan_id')
    company_id = fields.Many2one('res.company')
    state = fields.Selection([
        ('new', 'New'),
        ('done', 'Done')],default='new')
    attachment = fields.Binary()
    filename = fields.Char()
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('purchase.plan')
        return super(PurchasePlan, self).create(vals)

    @api.multi
    def make_purchase_order(self):
        view_id = self.env.ref('purchase.purchase_order_form')
        return {
            'name': _('New order'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'view_id': view_id.id,
            'views': [(view_id.id, 'form')],
            'context': {
                'default_origin': self.name,
                'company_id': self.company_id.id,
            }
        }


class PurchasePlanline(models.Model):
    _name = 'purchase.plan.line'
    plan_id = fields.Many2one('purchase.plan')
    product = fields.Many2one('product.product', required=True)
    description= fields.Char()
    qty = fields.Float()
    delivery_date = fields.Many2one('estimated.date')


class PurchaseOrderEdit(models.Model):
    _inherit = 'purchase.order'

    origin = fields.Char('Source Document', copy=False,readonly=True,
        help="Reference of the document that generated this purchase order "
             "request (e.g. a sales order)")

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('approved', 'Approved'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')

    @api.multi
    def initial_approve(self):
        self.state = 'approved'

    @api.multi
    def button_confirm(self):
        for order in self:
            if order.state not in ['approved']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step' \
                    or (order.company_id.po_double_validation == 'two_step' \
                        and order.amount_total < self.env.user.company_id.currency_id._convert(
                        order.company_id.po_double_validation_amount, order.currency_id, order.company_id,
                        order.date_order or fields.Date.today())) \
                    or order.user_has_groups('purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
        return True


    @api.constrains('origin')
    def purchase_order_in_plan(self):
        if self.origin:
            operation = self.env['purchase.plan'].search([('name', '=', self.origin)])
            l = []
            l.append(self.id)
            for record in operation:
                record.purchase_order = l


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    product_available = fields.Float(string="On Hand",related='product_id.qty_available')
    product_reserved = fields.Float(string="Reserved",related='product_id.outgoing_qty')
    net_available = fields.Float(string="Available",compute='get_product_quantity')

    @api.depends('product_id')
    def get_product_quantity(self):
        for rec in self:
            print("vskvmdlskmd")
            qty_available = rec.product_id.qty_available
            outgoing = rec.product_id.outgoing_qty
            print(qty_available - outgoing)
            rec.net_available = qty_available - outgoing