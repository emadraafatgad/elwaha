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
    availability = fields.Selection([('available', 'Available'), ('partially_available', 'partially_available'), ('waiting', 'Waiting'),('none', 'None')], string="Materials Availability",compute='_compute_availability',store=True)
    product_id = fields.Many2one('product.product', required=True)
    product_uom = fields.Many2one('uom.uom', required=True)
    product_qty = fields.Float(string='Quantity to Produce', required=True)
    raw_ids = fields.One2many('consumed.materials','manu_id')
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self._uid)
    date_planned_start = fields.Datetime(
        'Deadline Start', copy=False, default=fields.Datetime.now,
        index=True, required=True,
        states={'confirmed': [('readonly', False)]})
    qty_produced = fields.Float()

    @api.multi
    def action_check_availability(self):
        for mo in self:
            mo.raw_ids.action_available()

    @api.multi
    def action_produce(self):
        self.ensure_one()
        action = self.env.ref('logistics.act_actual_product_produce').read()[0]
        return action

    @api.multi
    @api.depends('raw_ids.state')
    def _compute_availability(self):
        for order in self:
            if not order.raw_ids:
                order.availability = 'none'
                continue
            raw_ids = order.raw_ids.filtered(lambda m: m.product_qty)
            partial_list = [x.state in ('partially_available', 'available') for x in raw_ids]
            assigned_list = [x.state in ('available', 'done', 'cancel') for x in raw_ids]
            order.availability = (all(assigned_list) and 'available') or (
                    any(partial_list) and 'partially_available') or 'waiting'

    @api.model
    def create(self, values):
        values['name'] = self.env['ir.sequence'].next_by_code('actual.manufacturing')
        return super(ActualManufacturing, self).create(values)

class ConsumedMaterials(models.Model):
    _name = 'consumed.materials'
    _description = 'Consumed Material'
    _rec_name = "product_id"
    manu_id = fields.Many2one('actual.manufacturing')
    plan_line_id = fields.Many2one('order.mrp.line')
    product_id = fields.Many2one('product.product', required=True)
    product_uom = fields.Many2one('uom.uom', required=True)
    product_qty = fields.Float(string='To Consume', required=True)
    reserved = fields.Float()
    qty_done = fields.Float()
    location_id = fields.Many2one('stock.location', required=True)
    location_dest_id = fields.Many2one('stock.location', required=True)
    state = fields.Selection(
        [('waiting', 'Waiting'), ('partiall_available', 'Partially Available'), ('available', 'Available'), ('done', 'Done')],
        string="status", default='waiting', track_visibility="onchange")
    @api.multi
    def action_available(self):
        for rec in self:
            qty = self.env['stock.quant'].search([
                ('product_id', '=', rec.product_id.id), ('location_id', '=', rec.location_id.id)])
            if qty.quantity >= rec.product_qty:
                rec.state = 'available'
                rec.reserved = rec.product_qty
                qty.quantity -= rec.product_qty
                qty.reserved_quantity += rec.product_qty
            elif qty.quantity != 0 and qty.quantity < rec.product_qty:
                rec.state = 'partially_available'
                rec.reserved = qty.quantity
                qty.quantity -= rec.qty.quantity
                qty.reserved_quantity += rec.qty.quantity


