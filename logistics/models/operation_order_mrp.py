from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import formatLang, DEFAULT_SERVER_DATETIME_FORMAT, datetime


class OperationOrderMRPPlan(models.Model):
    _name = 'operation.order.mrp'
    _inherit = ['operation.order', 'portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Order Manufacturing'
    _rec_name = 'code'

    _sql_constraints = [('order_no_uniq', 'unique (order_no)', 'Order no must be unique !')]

    code = fields.Char(default='/...')
    order_no = fields.Many2one('operation.order', string='Origin')
    state = fields.Selection([('new', 'New'), ('in_progress', 'In Progress'),('confirmed', 'Confirmed')], default='new', track_visibility="onchange")
    plan_lines = fields.One2many('order.mrp.line', 'plan_id')

    name = fields.Char('Order No', readonly=True, default='New')
    contract_no = fields.Char(readonly=True)
    status = fields.Selection([('new', 'New'), ('done', 'Done')], default='new')

    container_type = fields.Many2one('container.type', readonly=True,)
    reserve_no = fields.Char('Booking No', readonly=True,)
    estimated_arrival = fields.Date('ETA', readonly=True,)
    forwarder = fields.Many2one('res.partner', readonly=True, domain=[('partner_type', '=', 'forwarder')])
    shipping_line = fields.Many2one('res.partner', readonly=True, string="Shipping Line",
                                    domain=[('partner_type', '=', 'shipping_line')])
    container_no = fields.Float('Containers No', readonly=True,)
    uom = fields.Many2one('uom.uom', readonly=True,)
    container_weight = fields.Float('Container Weight',  readonly=True,)
    total_weight = fields.Float( string='Stander Quantity', readonly=True,)
    actual_qty= fields.Float("actual Quantity")
    container_bag_no = fields.Float( readonly=True,string="Container Bags NO.")
    total_bags = fields.Float(readonly=True,string="Total Bags")
    bag_type = fields.Char( readonly=True,)
    bill_of_lading = fields.Char( readonly=True,string="BL Ref.")
    packing = fields.Many2one('product.packing', readonly=True,)
    product = fields.Many2one('product.product', readonly=True, string='Commodity')

    location_id = fields.Many2one('stock.location', readonly=True,)
    exit_port = fields.Many2one('container.port', 'Containers Withdrawl Port', readonly=True,)
    shipment_port = fields.Many2one('container.port', 'POL', readonly=True, )
    arrival_port = fields.Many2one('container.port', 'POD', readonly=True,)
    loading_place = fields.Many2one('loading.place', readonly=True,)
    start_date = fields.Date('Start Loading Date', readonly=True,)
    end_date = fields.Date('Cut Off', readonly=True,)
    travel_date = fields.Date('Sailing Date', readonly=True,)
    delivery_date = fields.Date( readonly=True,)
    inspection_company1 = fields.Many2one('res.partner',  readonly=True, domain=[('partner_type', '=', 'inspection_company')])
    inspection_company2 = fields.Many2one('res.partner',  readonly=True, domain=[('partner_type', '=', 'inspection_company')])
    bank_certificate = fields.Char(readonly=True)
    customer_code = fields.Char(readonly=True, string='Client Code')
    # delivered_qty = fields.Float(string="Done QTY",)
    # notes = fields.Text()
    total_after_increase = fields.Float()
    clearance_finished = fields.Boolean()
    vessel_name = fields.Char()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)
    shipment_plan = fields.Many2one('delivery.plan', string="PLAN")

    @api.multi
    def action_create_mo(self):
        plan_lines = []
        if not self.plan_lines:
            raise ValidationError(_('You must enter lines.'))
        location_id = self.env['stock.location'].search([
            ('usage', '=', 'internal')])[0]
        location_dest_id = self.env['stock.location'].search([
            ('usage', '=', 'production')])[0]
        picking_type_id = self.env['stock.picking.type'].search([
            ('code', '=', 'mrp_operation')])[0]
        for line in self.plan_lines:
            plan_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'plan_line_id': line.id,
                'product_uom_qty': line.product_qty,
                'product_uom': line.product_uom.id,
                'location_id': location_id.id,
                'location_dest_id': location_dest_id.id,
            }))
        cr = self.env['stock.picking'].create({
            'location_id': location_id.id,
            'location_dest_id': location_dest_id.id,
            'picking_type_id': picking_type_id.id,
            'move_lines': plan_lines,
        })
        self.env['actual.manufacturing'].create({
            'product_id': self.product.id,
            'product_qty': self.total_weight,
            'product_uom': self.product.uom_id.id,
            'origin': self.id,
            'contract_no': self.contract_no,
            'picking_id': cr.id,

        })
        self.state = 'in_progress'

    show_delivery = fields.Boolean()
    delivery_count = fields.Integer(compute='_compute_delivery', string='Delivery', default=0)
    delivery_ids = fields.Many2many('stock.picking', compute='_compute_delivery', string='Delivery', copy=False)

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
                ('origin', '=', self.contract_no)
            ])
            line.delivery_ids = delivery
            line.delivery_count = len(delivery)

    @api.multi
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
                 'product_uom_qty': self.actual_qty,
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
        self.show_delivery = True
    @api.multi
    def action_confirm(self):
        """if not self.plan_lines:
            raise ValidationError(_('You must enter lines.'))
        bom_line = []
        for line in self.plan_lines:
            if line.product_qty <= 0:
                raise ValidationError(_('Qty of lines must be bigger than zero.'))
            bom_line.append((0, 0, {
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'product_uom_id': line.product_uom.id,

            }))
        bom = self.env['mrp.bom'].create({
            'product_tmpl_id': self.product.id,
            'product_uom_id': self.product.uom_id.id,
            'product_qty': self.total_weight,
            'plan_id': self.id,
            'type': 'normal',
            'bom_line_ids': bom_line,
        })
        self.env['mrp.production'].create({
            'bom_id': bom.id,
            'product_id': self.product.id,
            'product_qty': bom.product_qty,
            'product_uom_id': self.product.uom_id.id,
        })"""
        self.state = 'confirmed'

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.contract_no:
                raise ValidationError(_('You cannot delete %s as it comes from contract') % rec.name)
            if rec.state != 'new':
                raise ValidationError(_('You cannot delete %s as it is confirmed') % rec.name)

        return super(OperationOrderMRPPlan, self).unlink()

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('operation.order.mrp')
        return super(OperationOrderMRPPlan, self).create(vals)


class MRPPlanLine(models.Model):
    _name = 'order.mrp.line'

    plan_id = fields.Many2one('operation.order.mrp')
    product_id = fields.Many2one('product.product')
    product_qty = fields.Float()
    consumed = fields.Float()
    product_uom = fields.Many2one('uom.uom', related='product_id.uom_po_id', string='Product Uom')


class MRPBomInherit(models.Model):
    _inherit = 'mrp.bom'
    plan_id = fields.Many2one('operation.order.mrp', string='Order Plan', readonly=True)
