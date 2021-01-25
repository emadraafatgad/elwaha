from odoo import fields , api, models,_


class AppointmentConfiguration(models.Model):
    _name = "oeh.medical.config"

    name = fields.Char()
    visita = fields.Many2one('account.tax',string="VISITA Percentage")
    doctor_percentage = fields.Integer("DR Percentage")
    consultancy_price = fields.Integer("")
    doctor_min_charge = fields.Integer()
    clinic = fields.Many2one('res.company', 'Clinic', default=lambda self: self.env.user.company_id, ondelete='cascade')


class ClinicMachine(models.Model):
    _name = 'oeh.medical.machine'
    _inherit = ['mail.thread']

    name = fields.Char("Equipment Name")
    model = fields.Char('Model')
    serial_no = fields.Char('Serial Number', copy=False)
    effective_date = fields.Date('Effective Date', default=fields.Date.context_today, required=True,
                                 help="Date at which the equipment became effective. This date will be used to compute the Mean Time Between Failure.")
    cost = fields.Float('Cost')
    warranty_date = fields.Date('Warranty Expiration Date',)
    partner_id = fields.Many2one('res.partner', string='Vendor', domain="[('supplier', '=', 1)]")
    clinic = fields.Many2one('res.company', 'Clinic', default=lambda self: self.env.user.company_id, ondelete='cascade')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.name and record.serial_no:
                result.append((record.id, record.name + '/' + record.serial_no))
            if record.name and not record.serial_no:
                result.append((record.id, record.name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        equipment_ids = []
        if name:
            equipment_ids = self._search([('name', '=', name)] + args, limit=limit, access_rights_uid=name_get_uid)
        if not equipment_ids:
            equipment_ids = self._search([('name', operator, name)] + args, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(equipment_ids).name_get()


