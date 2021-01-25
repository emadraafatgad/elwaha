from odoo import fields, models, api


class ClinicMedicine(models.Model):
    _name = 'oeh.medical.medicine'
    _inherits = {
        'product.product': 'product_id',
    }

    product_id = fields.Many2one('product.product', string='Related Product', required=True, ondelete='cascade',
                                 help='Product-related data of the medicines')
    code = fields.Char()
    form = fields.Many2one('oeh.medical.medicine.form')
    # type = fields.Selection([
    #     ('consu', 'Consumable'),
    #     ('service', 'Service'),
    # ('product', 'Storable Product')], string='Product Type',required=True,
    #     help='A storable product is a product for which you manage stock. The Inventory app has to be installed.\n'
    #          'A consumable product is a product for which stock is not managed.\n'
    #          'A service is a non-material product you provide.')
    info = fields.Text(string='Extra Info')

    def update_quantity(self):
        print(self.qty_available)
        qty = self.qty_available - 1
        self.update({'qty_available':qty})
        print(self.qty_available)

    def action_update_quantity_on_hand(self):
        return self.product_tmpl_id.with_context({'default_product_id': self.product_id.id}).action_update_quantity_on_hand()


class MedicineForm(models.Model):
    _name = 'oeh.medical.medicine.form'

    name = fields.Char()


class ServiceMedicinePrice(models.Model):
    _name = 'oeh.medical.medicine.value'
    _description = "Information about the medicines"

    medicine_id = fields.Many2one('oeh.medical.medicine')
    quantity = fields.Integer()
    unit_price = fields.Integer()
    total_price = fields.Integer()
    service_line_id = fields.Many2one('ohe.medical.service.line')
    service_id = fields.Many2one('oeh.medical.service')