from odoo import fields, api, models, _


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    advanced_payment = fields.Float()
    bl_no = fields.Char()
    ship_date = fields.Date()
    ship_via = fields.Char()
    pol = fields.Many2one('container.port', string='Port Of Loading')
    pod = fields.Many2one('container.port', string='Port Of Discharge')
    vessel_voyage_no = fields.Char(string='Vessel & Voyage No')

    @api.multi
    def action_invoice_open(self):
        origin = self.env['operation.order'].search([('name', '=', self.origin)])
        for org in origin:
            org.invoice_id = self.id
        return super(AccountInvoice, self).action_invoice_open()

