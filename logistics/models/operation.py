from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OperationOrder(models.Model):
    _name = 'operation.order'
    _description = 'Operation Order'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char('Order No', track_visibility="onchange", default='New')
    _sql_constraints = [('name_uniq', 'unique (name)', 'Sequence Must Be Unique')]

    contract_no = fields.Char(track_visibility="onchange")
    contract_id = fields.Many2one('sale.order',related='shipment_plan.contract_id',store=True)
    contract_date = fields.Date(related='shipment_plan.contract_date',store=True)
    status = fields.Selection([('new', 'New'), ('done', 'Done')], track_visibility="onchange", default='new')
    state = fields.Selection(
        [('new', 'New'), ('confirmed', 'Under Stuffing'), ('waiting_port', 'Waiting At Port'), ('sailed', 'Sailed')],
        default='new', track_visibility="onchange")
    container_type = fields.Many2one('container.type', track_visibility="onchange", )
    reserve_no = fields.Char('Booking No', track_visibility="onchange", )
    estimated_arrival = fields.Date('ETA', track_visibility="onchange", )
    forwarder = fields.Many2one('res.partner', track_visibility="onchange", domain=[('partner_type', '=', 'forwarder')])
    shipping_line = fields.Many2one('res.partner', track_visibility="onchange", string="Shipping Line",
                                    domain=[('partner_type', '=', 'shipping_line')])
    container_no = fields.Float('Containers No', track_visibility="onchange", required=True)
    uom = fields.Many2one('uom.uom', track_visibility="onchange", )
    commodity_type = fields.Many2one('commodity.type', track_visibility="onchange", )
    container_weight = fields.Float('Container Weight', track_visibility="onchange", digits=(16, 3), )
    total_weight = fields.Float(compute='compute_total', track_visibility="onchange", digits=(16, 3),
                                string='Stander Quantity')
    qty_done = fields.Float(readonly=True)
    amount = fields.Float(compute='compute_amount', track_visibility="onchange", digits=(16, 3), )
    container_bag_no = fields.Float(string="Container Bags NO.", track_visibility="onchange", digits=(16, 3), )
    total_bags = fields.Float(string="Total Bags")
    bag_type = fields.Char(track_visibility="onchange", )
    bill_of_lading = fields.Char(track_visibility="onchange", string="BL Ref.")
    packing = fields.Many2one('product.packing', track_visibility="onchange", )
    product = fields.Many2one('product.product', track_visibility="onchange", required=True, string='Commodity',
                              compute="get_all_fields")

    def default_location_id(self):
        location = self.env['stock.location'].search([('usage', '=', 'internal')])
        return location[0]

    @api.depends('travel_date')
    def get_default_cutt_of_date(self):
        for rec in self:
            if rec.travel_date:
                # print(rec.travel_date)
                cutt_of_date = rec.travel_date - relativedelta(days=4)
                # print(cutt_of_date,type(cutt_of_date),"loooool")
                rec.end_date = cutt_of_date

    @api.depends('travel_date')
    def get_loading_date(self):
        for rec in self:
            if rec.travel_date:
                loading_date = rec.travel_date - relativedelta(days=6)
                rec.start_date = loading_date

    location_id = fields.Many2one('stock.location', required=True, default=default_location_id)
    exit_port = fields.Many2one('container.port', 'Containers Withdrawl Port')
    shipment_port = fields.Many2one('container.port', 'POL')
    arrival_port = fields.Many2one('container.port', 'POD', compute="get_all_fields")
    loading_place = fields.Many2one('loading.place')
    invoice_id = fields.Many2one('account.invoice')
    invoice_no = fields.Char('Invoice Number', related='invoice_id.number')
    price_unit = fields.Monetary('Unit Price', required=True, currency_field='currency_id', compute="get_all_fields")
    currency_id = fields.Many2one('res.currency', compute="get_all_fields", store=True, string='Currency')
    start_date = fields.Date('Start Loading Date', compute='get_loading_date')
    end_date = fields.Date('Cut Off', compute='get_default_cutt_of_date')
    travel_date = fields.Date('Sailing Date')
    delivery_date = fields.Date()
    inspection_company1 = fields.Many2one('res.partner', domain=[('partner_type', '=', 'inspection_company')])
    inspection_company2 = fields.Many2one('res.partner', domain=[('partner_type', '=', 'inspection_company')])
    customer = fields.Many2one('res.partner', related='shipment_plan.partner_id',
                               domain=[('partner_type', '=', 'client')])
    agree = fields.Char()
    bank_certificate = fields.Char()
    customer_code = fields.Char(readonly=True, string='Client Code', related='customer.client_code')
    delivered_qty = fields.Float(string="Net Weight", digits=(16, 3), )
    gross_weight = fields.Float(string="Gross Weight", digits=(16, 3), )
    notes = fields.Text()
    total_after_increase = fields.Float(compute='compute_total_after_increase', digits=(16, 3), )
    clearance_finished = fields.Boolean()
    vessel_name = fields.Char()
    company_id = fields.Many2one('res.company')
    shipment_plan = fields.Many2one('delivery.plan', string="PLAN", required=True)

    @api.model
    def _get_product_id_domain(self):
        res = [('id', 'in', [0])]  # Nothing accepted by domain, by default
        delivery_lines = self.env['delivery.plan.line']
        if self.contract_id:
            print("i am in")
            delivery_lines = delivery_lines.search([('contract_id', '=', self.contract_id)]).ids
            print(delivery_lines)
            res = [('id', 'in', delivery_lines)]
            print(res, "res")
        return res

    shipment_plan_line_id = fields.Many2one('delivery.plan.line', string="Commodity",
                                            domain="[('contract_id','=',contract_id)]")

    # domain="[('id','in',shipment_plan.shipment_lines.ids)]")
    # domain = lambda self: self._get_employee_id_domain())

    @api.depends('shipment_plan_line_id')
    def get_all_fields(self):
        for rec in self:
            # print(rec.shipment_plan,rec.shipment_plan.name,rec._context.get('active_id'))
            contract_line = rec.shipment_plan_line_id
            rec.product = contract_line.product_id
            # rec.packing = contract_line.packing
            rec.arrival_port = contract_line.to_port
            # rec.exit_port = contract_line.from_port
            # rec.shipment_port = contract_line.from_port
            rec.price_unit = contract_line.price_unit
            rec.currency_id = contract_line.currency_id

    @api.onchange('shipment_plan')
    def onchange_shipment_plan(self):
        if self.shipment_plan:
            self.company_id = self.shipment_plan.company_id.id

    @api.constrains('shipment_plan')
    def constrains_shipment_plan(self):
        if self.shipment_plan:
            self.company_id = self.shipment_plan.company_id.id

    @api.constrains('total_weight')
    def const_line_ids(self):
        qty = 0.0
        for line in self.shipment_plan.line_ids:
            qty += line.total_weight
        if qty > self.shipment_plan.quantity:
            raise ValidationError(_('Quantities of lines are not equal Total Quantity %') % self.quantity)

    @api.depends('price_unit', 'total_weight')
    def compute_amount(self):
        for rec in self:
            rec.amount = rec.price_unit * rec.total_weight

    @api.depends('amount')
    def compute_total_after_increase(self):
        for rec in self:
            rec.total_after_increase = rec.amount + (rec.amount * 10 * 0.01)

    def compute_delivered_qty(self):
        delivery = self.env['stock.picking'].search([('origin', '=', self.name)])
        for record in delivery:
            for rec in record.move_lines:
                self.delivered_qty += rec.quantity_done

    @api.depends('container_no', 'container_weight')
    def compute_total(self):
        for rec in self:
            rec.total_weight = rec.container_no * rec.container_weight

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        if not self.reserve_no:
            raise ValidationError(_('You must enter booking no.'))
        if not self.forwarder:
            raise ValidationError(_('You must enter Forwarder.'))
        if not self.shipping_line:
            raise ValidationError(_('You must enter shipping line.'))
        if self.container_no <= 0:
            raise ValidationError(_('Container no must be bigger than Zero.'))
        if self.container_weight <= 0:
            raise ValidationError(_('Container weight must be bigger than Zero.'))
        if not self.loading_place:
            raise ValidationError(_('You must enter loading Place.'))
        if not self.travel_date:
            raise ValidationError(_('You must enter start sailing date.'))
        if not self.price_unit:
            raise ValidationError(_('You must enter unit rate.'))
        self.env['operation.order.mrp'].create({
            'order_no': self.id,
            'shipment_plan': self.shipment_plan.id,
            'product': self.product.id,
            'shipment_plan_line_id': self.shipment_plan_line_id.id,
            'packing': self.packing.id,
            'contract_no': self.contract_no,
            'reserve_no': self.reserve_no,
            'shipping_line': self.shipping_line.id,
            'forwarder': self.forwarder.id,
            'container_type': self.container_type.id,
            'container_no': self.container_no,
            'container_weight': self.container_weight,
            'container_bag_no': self.container_bag_no,
            'bag_type': self.bag_type,
            'loading_place': self.loading_place.id,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'notes': self.notes,
            'travel_date': self.travel_date,
            'inspection_company1': self.inspection_company1.id,
            'inspection_company2': self.inspection_company2.id,
            'company_id': self.company_id.id,
        })
        self.status = 'done'
        self.state = 'confirmed'

    @api.multi
    def update_mrp(self):
        self.ensure_one()
        for rec in self:
            if not rec.reserve_no:
                raise ValidationError(_('You must enter booking no.'))
            if not rec.forwarder:
                raise ValidationError(_('You must enter Forwarder.'))
            if not rec.shipping_line:
                raise ValidationError(_('You must enter shipping line.'))
            if rec.container_no <= 0:
                raise ValidationError(_('Container no must be bigger than Zero.'))
            if rec.container_weight <= 0:
                raise ValidationError(_('Container weight must be bigger than Zero.'))
            if not rec.loading_place:
                raise ValidationError(_('You must enter loading Place.'))
            if not rec.travel_date:
                raise ValidationError(_('You must enter start sailing date.'))
            if not rec.price_unit:
                raise ValidationError(_('You must enter unit rate.'))
            mrp_order_id =  self.env['operation.order.mrp'].search([('order_no','=' ,rec.id)])
            print(mrp_order_id)
            print("mrp_order_id", rec.packing.name,)
            values ={
                'packing': rec.packing.id,
                'contract_no': rec.contract_no,
                'reserve_no': rec.reserve_no,
                'shipping_line': rec.shipping_line.id,
                'forwarder': rec.forwarder.id,
                'container_type': rec.container_type.id,
                'container_no': rec.container_no,
                'container_weight': rec.container_weight,
                'container_bag_no': rec.container_bag_no,
                'bag_type': rec.bag_type,
                'loading_place': rec.loading_place.id,
                'start_date': rec.start_date,
                'end_date': rec.end_date,
                'notes': rec.notes,
                'travel_date': rec.travel_date,
                'inspection_company1': rec.inspection_company1.id,
                'inspection_company2': rec.inspection_company2.id,
            }
            print(values)
            mrp_order_id.write(values)

    show = fields.Boolean()
    show_delivery = fields.Boolean()
    invoice_count = fields.Integer(compute='_compute_invoice', string='Invoice', default=0)
    invoice_ids = fields.Many2many('account.invoice', compute='_compute_invoice', string='Invoice', copy=False)
    delivery_count = fields.Integer(compute='_compute_delivery', string='Delivery', default=0)
    delivery_ids = fields.Many2many('stock.picking', compute='_compute_delivery', string='Delivery', copy=False)

    def action_view_invoice(self):
        action = self.env.ref('account.action_invoice_tree1')
        result = action.read()[0]
        result.pop('id', None)
        result['context'] = {}
        inv_ids = sum([line.invoice_ids.ids for line in self], [])
        if len(inv_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, inv_ids)) + "])]"
        elif len(inv_ids) == 1:
            res = self.env.ref('account.invoice_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = inv_ids and inv_ids[0] or False
        return result

    def _compute_invoice(self):
        for line in self:
            invoices = self.env['account.invoice'].search([
                ('origin', '=', self.name)
            ])
            line.invoice_ids = invoices
            line.invoice_count = len(invoices)

    def action_view_delivery(self):
        action = self.env.ref('stock.action_picking_tree_ready')
        result = action.read()[0]
        result.pop('id', None)
        result['context'] = {}
        del_ids = sum([line.delivery_ids.ids for line in self], [])
        if len(del_ids) > 1:
            result['domain'] = "[('id','in',[" + ','.join(map(str, del_ids)) + "])]"
        elif len(del_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = del_ids and del_ids[0] or False
        return result

    def _compute_delivery(self):
        for line in self:
            delivery = self.env['stock.picking'].search([
                ('origin', '=', self.name)
            ])
            line.delivery_ids = delivery
            line.delivery_count = len(delivery)

    @api.multi
    def action_invoice(self):
        invoice_line = []
        sale_journal = self.env['account.journal'].search([('type', '=', 'sale')])[0]
        accounts = self.product.product_tmpl_id.get_product_accounts()
        invoice_line.append((0, 0, {
            'product_id': self.product.id,
            'name': self.product.name,
            'product_uom_id': self.product.uom_id.id,
            'price_unit': self.price_unit,
            'discount': 0.0,
            'quantity': self.delivered_qty,
            'account_id': accounts.get('stock_input') and accounts['stock_input'].id or \
                          accounts['income'].id,
        }))
        vessel_voyage = self.vessel_name + ',' + self.vessel_name
        cr = self.env['account.invoice'].create({
            'partner_id': self.customer.id,
            'state': 'draft',
            'type': 'out_invoice',
            'origin': self.contract_no,
            'bl_no': self.bill_of_lading,
            'ship_date': self.travel_date,
            'travel_date': self.travel_date,
            'pol': self.shipment_port.id,
            'pod': self.arrival_port.id,
            'vessel_voyage_no': vessel_voyage,
            'packing': self.packing.id,
            'gross_weight': self.gross_weight,
            'container_no': self.container_no,
            'currency_id': self.currency_id.id if self.currency_id else 2,
            'journal_id': sale_journal.id,
            'account_id': self.customer.property_account_receivable_id.id,
            'invoice_line_ids': invoice_line,
        })
        self.invoice_id = cr.id
        self.show = True

    """@api.multi
    def action_deliver(self):
        copy_record = self.env['stock.picking']
        sp_types = self.env['stock.picking.type'].search([('code', '=', 'outgoing')])
        order_lines = []
        order_lines.append(
            (0, 0,
             {
                 'name': self.product.name,
                 'product_id': self.product.id,
                 'product_uom': self.product.uom_id.id,
                 'date_expected': datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                 'product_uom_qty': self.total_weight,
             }
             ))

        dest_location = self.env['stock.location'].search([
            ('usage', '=', 'customer')

        ])
        picking = copy_record.create({
            'origin': self.contract_no,
            'priority': '1',
            'state': 'assigned',
            'move_lines': order_lines,
            'location_id': self.location_id.id,
            'location_dest_id': dest_location[0].id,
            'picking_type_id': sp_types[0].id,
            'partner_id': self.customer.id,
        }).action_assign()
        self.show_delivery = True"""

    # @api.multi
    # def unlink(self):
    #     for rec in self:
    #         if rec.contract_no:
    #             raise ValidationError(_('You cannot delete %s as it comes from contract') % rec.name)
    #         if rec.state != 'new':
    #             raise ValidationError(_('You cannot delete %s as it is confirmed') % rec.name)
    # return super(OperationOrder, self).unlink()

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('operation.order')
        return super(OperationOrder, self).create(vals)
