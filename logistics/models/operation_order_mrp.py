from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OperationOrderMRPPlan(models.Model):
    _name = 'operation.order.mrp'
    _inherit = ['operation.order', 'portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Order Manufacturing'
    _rec_name = 'code'

    _sql_constraints = [('order_no_uniq', 'unique (order_no)', 'Order no must be unique !')]

    code = fields.Char(default='/...')
    order_no = fields.Many2one('operation.order', string='Origin')
    state = fields.Selection([('new', 'New'), ('confirmed', 'Confirmed')], default='new', track_visibility="onchange")
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
    company_id = fields.Many2one('res.company')

    shipment_plan = fields.Many2one('delivery.plan', string="PLAN")

    @api.multi
    def action_confirm(self):
        if not self.plan_lines:
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
        })
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
    product_uom = fields.Many2one('uom.uom', related='product_id.uom_po_id', string='Product Uom')


class MRPBomInherit(models.Model):
    _inherit = 'mrp.bom'
    plan_id = fields.Many2one('operation.order.mrp', string='Order Plan', readonly=True)
