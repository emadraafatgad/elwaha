# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_round

class ActualProductProduce(models.TransientModel):
    _name = "actual.product.produce"
    _description = "Record Production"

    production_id = fields.Many2one('actual.manufacturing', 'Production')
    product_id = fields.Many2one('product.product', 'Product')
    product_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True)
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure')
    produce_line_ids = fields.One2many('actual.product.produce.line', 'product_produce_id', string='Product to Track')
    @api.model
    def default_get(self, fields):
        res = super(ActualProductProduce, self).default_get(fields)
        if self._context and self._context.get('active_id'):
            production = self.env['actual.manufacturing'].browse(self._context['active_id'])
            todo_uom = production.product_uom.id
            todo_quantity = production.product_qty - production.qty_produced
            if 'production_id' in fields:
                res['production_id'] = production.id
            if 'product_id' in fields:
                res['product_id'] = production.product_id.id
            if 'product_uom_id' in fields:
                res['product_uom_id'] = todo_uom
            if 'product_qty' in fields:
                res['product_qty'] = todo_quantity
        lines=[]
        for record in production.move_lines:
            qty_to_consume = record.product_uom_qty - record.quantity_done
            lines.append(
                (0, 0,
                 {
                     'product_id': record.product_id.id,
                     'qty_to_consume': qty_to_consume,
                     'qty_reserved': qty_to_consume,
                     'qty_done': qty_to_consume,
                     'product_uom_id': record.product_uom.id,
                     'consumed_raw_id': record.id,
                     'plan_raw_id': record.plan_line_id.id,
                 }
                 ))
        res['produce_line_ids'] = lines
        return res
    @api.multi
    def do_produce(self):
        quantity = self.product_qty
        if float_compare(quantity, 0, precision_rounding=self.product_uom_id.rounding) <= 0:
            raise UserError(_("The production order for '%s' has no quantity specified.") % self.product_id.display_name)
        production = self.env['actual.manufacturing'].browse(self._context['active_id'])
        production.qty_produced += quantity
        production.origin.actual_qty += quantity
        production.origin.order_no.qty_done += quantity
        for rec in self.produce_line_ids:
            rec.consumed_raw_id.quantity_done += rec.qty_done
            rec.plan_raw_id.consumed += rec.qty_done
        production.state = 'in_progress'
        return {'type': 'ir.actions.act_window_close'}


class MrpProductProduceLine(models.TransientModel):
    _name = "actual.product.produce.line"
    _description = "Record Production Line"

    product_produce_id = fields.Many2one('actual.product.produce')
    consumed_raw_id = fields.Many2one('stock.move')
    plan_raw_id = fields.Many2one('order.mrp.line')
    product_id = fields.Many2one('product.product', 'Product')
    qty_to_consume = fields.Float('To Consume', digits=dp.get_precision('Product Unit of Measure'))
    product_uom_id = fields.Many2one('uom.uom', 'Unit of Measure')
    qty_done = fields.Float('Consumed', digits=dp.get_precision('Product Unit of Measure'))
    qty_reserved = fields.Float('Reserved', digits=dp.get_precision('Product Unit of Measure'))

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.product_uom_id = self.product_id.uom_id.id

    @api.onchange('qty_to_consume')
    def _onchange_qty_to_consume(self):
        self.qty_reserved = self.qty_to_consume
