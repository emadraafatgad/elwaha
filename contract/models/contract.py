from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, date, time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class contract(models.Model):
    _inherit = 'sale.order'
    _order = 'create_date desc'

    partial_shipment = fields.Selection([
        ('allowed', 'Allowed'),
        ('not_allowed', 'Not Allowed')], required=True)

    name = fields.Char(default='')
    date_order = fields.Date(string="Contract Date")
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', required=False,readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Pricelist for current sales order.")
    currency_id = fields.Many2one("res.currency", string="Currency",store=True, readonly=False,  required=True)
    date_string = fields.Char()
    inspection_company = fields.Many2one('res.partner', domain=[('partner_type', '=', 'inspection_company')])
    margin = fields.Float(string="Tolerance Margin", default=10)
    attachment = fields.Binary()
    filename = fields.Char()
    incoterm_id = fields.Many2one('account.incoterms', 'Incoterms',
        help="International Commercial Terms are a series of predefined commercial terms used in international transactions.")

    # product = fields.Many2many('product.product',string="Commodity", required=True,store=True)
    # total_qty = fields.Float(required=True,string="QTY")
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
    ], string='Invoice Status', compute='_get_invoiced', store=True, readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Editing'),
        ('done', 'InProgress'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3,
        default='draft')
    customer_code = fields.Char()
    company_name = fields.Char()


    # @api.multi
    # @api.onchange('date_order')
    # def _onchange_date_order(self):
    #     for rec in self:
    #         date = datetime.strptime(str(rec.date_order), DEFAULT_SERVER_DATE_FORMAT)
    #         day = date.day
    #         if day < 10:
    #             day = '0'+str(day)
    #         month = date.month
    #         if month < 10:
    #             month = '0'+str(month)
    #         year = date.year
    #         rec.date_string = str(day) + str(month) + str(year)[-2:]

    @api.multi
    @api.onchange('company_id', 'partner_id')
    def _onchange_customer_company(self):
        for rec in self:
            rec.customer_code = rec.partner_id.client_code
            rec.company_name = rec.company_id.name

    @api.multi
    def action_confirm(self):
        order_line = []
        shipment_line = []
        l = []
        for rec in self.order_line:
            shipment_line.append((0, 0, {
                'product_id': rec.product_id.id,
                'description': rec.name,
                'quantity': rec.product_uom_qty,
                'price_unit': rec.price_unit,
                'delivery_date': rec.delivery_date.id,
                'from_port': rec.from_port.id,
                'to_port': rec.to_port.id,
                'packing': rec.packing.id,
                'contract_id': rec.order_id.id,
            }))
            order_line.append((0, 0, {
                'product': rec.product_id.id,
                'description': rec.name,
                'qty': rec.product_uom_qty,
                'delivery_date': rec.delivery_date.id,
            }))
        # for record in self.product:
        #     l.append(record.id)
        self.env['delivery.plan'].create({
            'partner_id': self.partner_id.id,
            'origin': self.name,
            'company_id': self.company_id.id,
            'contract_id': self.id,
            'partial_shipment': self.partial_shipment,
            'shipment_lines': shipment_line,
        }).get_attachments()

        print("iam to purchase")
        if self.attachment:
            self.env['purchase.plan'].create({
                'origin': self.name,
                'company_id': self.company_id.id,
                # 'total_qty': self.total_qty,
                'product': [(6, 0, l)],
                'line_ids': order_line,

            })
        return super(contract, self).action_confirm()

    @api.multi
    def action_update(self):
        purchase_order_line = []
        shipment_line = []
        l = []
        delivery_plan = self.env['delivery.plan'].search([('origin', '=', self.name)])
        purchase_plan = self.env['purchase.plan'].search([('origin', '=', self.name)])
        for rec in self.order_line:
            purchase_order_line.append((0, 0, {
                'product': rec.product_id.id,
                'description': rec.name,
                'qty': rec.product_uom_qty,
                'delivery_date': rec.delivery_date.id,
            }))
            if not rec.product_id:
                raise ValidationError('There is No Commodity')
            elif not rec.name:
                raise  ValidationError('There is NO Description')
            elif rec.quantity <= 1:
                raise  ValidationError('There is NO Quantity')
            elif not rec.delivery_date:
                raise  ValidationError('There is NO Delivery Date')
            elif not rec.from_port:
                raise  ValidationError('There is NO POL')
            elif not rec.to_port:
                raise  ValidationError('There is NO POD')
            elif not rec.packing:
                raise  ValidationError('There is NO Packing')

            shipment_line.append((0,0,{
                'product_id': rec.product_id.id,
                'description': rec.name,
                'quantity': rec.product_uom_qty,
                'price_unit': rec.price_unit,
                'currency_id': rec.currency_id.id,
                'delivery_date': rec.delivery_date.id,
                'from_port': rec.from_port.id,
                'to_port': rec.to_port.id,
                'packing': rec.packing.id,
                # 'contract_id': rec.order_id.id
            }))
        for rec in delivery_plan.line_ids:
            rec.unlink()
        for record in delivery_plan.shipment_lines :
            record.unlink()
        purchase_plan.write({
            'origin': self.name,
            'filename': self.filename,
            'company_id': self.company_id.id,
            'line_ids': purchase_order_line})

        delivery_plan.write({
            'partner_id': self.partner_id.id,
            'origin': self.name,
            'company_id': self.company_id.id,
            'partial_shipment': self.partial_shipment,
            'shipment_lines': shipment_line,
        })
        delivery_plan.get_attachments()

        # delivery_plan.shipment_lines = [(5, 0, delivery_plan.shipment_lines )]
        # delivery_plan.shipment_lines = shipment_line

    @api.depends('state', 'order_line.invoice_status', 'order_line.invoice_lines')
    def _get_invoiced(self):
        self.invoice_status = 'no'

    # @api.constrains('order_line','total_qty')
    # def _const_qty(self):
    #     total = 0.0
    #     for line in self.order_line:
    #         total += line.product_uom_qty
    #         if line.product_id not in self.product:
    #             raise ValidationError(_('Products in lines must be one of the products above (%s) ') % line.product_id.name)
    #     if total != self.total_qty:
    #         raise ValidationError(_('Sorry, Not Acceptable  total quantity of lines must be: %s') % self.total_qty)

    @api.onchange('partner_id')
    def partner_code(self):
        if self.partner_id:
            if not self.partner_id.client_code:
                warning = {
                    'title': _('Warning!'),
                    'message': _('This customer has not a short code!'),
                }
                return {'warning': warning}

    # @api.model
    # def create(self, vals):
        # seq = self.env['ir.sequence'].next_by_code('contract.order')
        # customer_code = vals.get('customer_code') or ''
        # company_name = vals.get('company_name')
        # date_string = vals.get('date_string')
        # vals['name'] = customer_code + '.' + company_name + '. /' + date_string + seq
        # return super(contract, self).create(vals)


class OrderLineContract(models.Model):
    _inherit = 'sale.order.line'

    product_uom_qty = fields.Float(string='Ordered Quantity', required=True, default=0.0)
    container_no = fields.Integer('Container No')
    container_type = fields.Many2one('container.type')
    commodity_type = fields.Many2one('commodity.type')
    packing = fields.Many2one('product.packing', string='Packing')
    inspection_company = fields.Many2one('res.partner', related='order_id.inspection_company',
                                         domain=[('partner_type', '=', 'inspection_company')])
    delivery_date = fields.Many2one('estimated.date', string="ETD")
    from_port = fields.Many2one('container.port', string='POL')
    to_port = fields.Many2one('container.port', string='POD')

    def get_sale_order_line_multiline_description_sale(self, product):
        """ Compute a default multiline description for this sales order line.
        This method exists so it can be overridden in other modules to change how the default name is computed.
        In general only the product is used to compute the name, and this method would not be necessary (we could directly override the method in product).
        BUT in event_sale we need to know specifically the sales order line as well as the product to generate the name:
            the product is not sufficient because we also need to know the event_id and the event_ticket_id (both which belong to the sale order line).
        """
        return False

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        """Retrieve the price before applying the pricelist
            :param obj product: object of current product record
            :parem float qty: total quentity of product
            :param tuple price_and_rule: tuple(price, suitable_rule) coming from pricelist computation
            :param obj uom: unit of measure of current order line
            :param integer pricelist_id: pricelist id of sales order"""
        currency_id = self.currency_id
        return 0, currency_id

    @api.multi
    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        # awa: don't know if it's still the case since we need the "product_no_variant_attribute_value_ids" field now
        # to be able to compute the full price

        # it is possible that a no_variant attribute is still in a variant if
        # the type of the attribute has been changed after creation.

        return max(0, 0)
    # @api.onchange('product_id')
    # def _onchange_order_line_Product(self):
    #     for line in self:
    #         if line.product_id:
    #          if line.product_id not in self.order_id.product:
    #             raise ValidationError(_('You must select same commodity as above'))

    # @api.onchange('product_id')
    # def _onchange_order_line_product(self):
    #
    #     qty = self.order_id.total_qty
    #     product = self.order_id.product
    #     if not product:
    #         warning = {
    #             'title': _('Warning!'),
    #             'message': _('You must first Select commodity above.'),
    #         }
    #         return {'warning': warning}
    #     if qty <= 0:
    #         warning = {
    #             'title': _('Warning!'),
    #             'message': _('You must first enter total qty.'),
    #         }
    #         return {'warning': warning}

    # @api.onchange('product_id')
    # def _onchange_qty(self):
    #     total=0.0
    #     for line in self.order_id.order_line:
    #         total += line.product_uom_qty
    #     if self.product_id and total == self.order_id.total_qty:
    #         raise ValidationError(_('Sorry, Not Acceptable  total quantity must be: %s') % self.order_id.total_qty)


class ProductPacking(models.Model):
    _name = 'product.packing'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Packing'

    name = fields.Char(string="Name", required=True)


class ContainerPort(models.Model):
    _name = 'container.port'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Port'
    _rec_name = 'combination'

    combination = fields.Char(string='Combination', compute='_compute_fields_combination')

    @api.depends('name', 'country_id')
    def _compute_fields_combination(self):
        for test in self:
            test.combination = test.name + '/ ' + test.country_id.name

    name = fields.Char(string="Name", required=True)
    country_id = fields.Many2one('res.country', required=True)


class ContainerType(models.Model):
    _name = 'container.type'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Container Type'

    name = fields.Char('Name', required=True)


class CommodityType(models.Model):
    _name = 'commodity.type'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True)


class EstimatedDate(models.Model):
    _name = 'estimated.date'

    name = fields.Char(required=True)


class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    suppose_qty = fields.Float()


class Partner(models.Model):
    _inherit = 'res.partner'

    client_code = fields.Char()
    _sql_constraints = [
        ('client_code_uniq', 'unique (client_code)', 'Client code must be unique!')]

    partner_type = fields.Selection(
        [('forwarder', 'Forwarder'), ('shipping_line', 'Shipping Line'), ('inspection_company', 'Inspection Company'),
         ('bank', 'Bank'), ('client', 'Client')])

    @api.onchange('partner_type')
    def onchange_partner_type(self):
        if self.partner_type == 'client':
            self.customer = True
            self.supplier = False
        else:
            self.customer = False
            self.supplier = True


class Pricelist(models.Model):
    _inherit = "product.pricelist"

    @api.multi
    def name_get(self):
        return [(pricelist.id, '%s' % (pricelist.currency_id.name)) for pricelist in self]
