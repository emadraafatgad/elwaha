from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ActualManufacturing(models.Model):
    _name = 'actual.manufacturing'
    _description = 'Manufacturing'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    name = fields.Char('Reference', default='New', readonly=True)
    origin = fields.Many2one('operation.order.mrp')
    contract_no = fields.Char()
    state = fields.Selection([('confirmed', 'Confirmed'), ('in_progress', 'In Progress'), ('done', 'Done'),('cancel', 'Cancelled')], string="status", default='confirmed',track_visibility="onchange")
    #availability = fields.Selection([('available', 'Available'), ('partially_available', 'partially_available'), ('waiting', 'Waiting'),('none', 'None')], string="Materials Availability",compute='_compute_availability',store=True)
    product_id = fields.Many2one('product.product', required=True)
    product_uom = fields.Many2one('uom.uom', required=True)
    product_qty = fields.Float(string='Quantity to Produce', required=True)
    #raw_ids = fields.One2many('consumed.materials','manu_id')
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self._uid)
    date_planned_start = fields.Datetime(
        'Deadline Start', copy=False, default=fields.Datetime.now,
        index=True, required=True,
        states={'confirmed': [('readonly', False)]})
    manu_picking_id = fields.Many2one('stock.move')
    qty_produced = fields.Float()
    picking_id = fields.Many2one('stock.picking')
    picking_state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], related='picking_id.state',store=True)
    move_lines = fields.One2many('stock.move','manufacturing_id',compute='compute_move_lines')
    @api.depends('picking_id')
    def compute_move_lines(self):
        moves = self.env['stock.move'].search([
            ('picking_id', '=', self.picking_id.id)])
        self.move_lines= moves

    compute_produce = fields.Boolean(compute='_compute_produce')
    @api.depends('move_lines')
    def _compute_produce(self):
        self.compute_produce = all(line.product_uom_qty == line.quantity_done for line in self.move_lines)

    @api.multi
    def action_check_availability(self):
        self.picking_id.action_assign()

    availability = fields.Boolean(compute='compute_availability')

    @api.depends('move_lines')
    def compute_availability(self):
        self.availability = all(line.product_uom_qty == line.reserved_availability for line in self.move_lines) or self.picking_state in ('done','cancel')

    @api.multi
    def action_produce(self):
        self.ensure_one()
        action = self.env.ref('logistics.act_actual_product_produce').read()[0]
        return action

    @api.multi
    def action_post_inventory(self):
        self.picking_id.button_validate()

    @api.multi
    def action_done(self):
        self.state = 'done'
    check_done = fields.Boolean(compute='_check_done')
    @api.depends('picking_id','state')
    def _check_done(self):
        if self.picking_id.state == 'done' and self.state == 'in_progress':
            self.check_done = True
        else:
            self.check_done = False


    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('actual.manufacturing')
        return super(ActualManufacturing, self).create(values)

class ActualManufacturingStockMOve(models.Model):
    _inherit = 'stock.move'
    manufacturing_id = fields.Many2one('actual.manufacturing')
    plan_line_id = fields.Many2one('order.mrp.line')


