from odoo import api, fields, models, _


class OeHealthPhysician(models.Model):
    _name = "oeh.medical.physician"
    _description = "Information about the doctor"
    _inherits={'hr.employee': 'employee_id',}

    employee_id = fields.Many2one('hr.employee', string='Related Employee', required=True, ondelete='cascade', help='Employee-related data of the physician')
    clinic = fields.Many2many('res.company', string='clinic', help="Clinic where doctor works")
    code = fields.Char(string='Licence ID', size=128, help="Physician's License ID")
    oeh_user_id = fields.Many2one('res.users', string='Responsible Odoo User')
    minimum_charge = fields.Float()
    consultancy_price = fields.Integer("")

    _sql_constraints = [
        ('code_oeh_physician_userid_uniq', 'unique(oeh_user_id)', "Selected 'Responsible' user is already assigned to another physician !")
    ]

    read_only = fields.Boolean(compute='_cac')

    @api.multi
    def _cac(self):
        print(self.env.user.has_group('purchase.group_purchase_manager'))
        self.read_only = self.env.user.has_group('purchase.group_purchase_manager')

    @api.onchange('state_id')
    def onchange_state(self):
        if self.state_id:
            self.country_id = self.state_id.country_id.id

    @api.onchange('address_id')
    def _onchange_address(self):
        self.work_phone = self.address_id.phone
        self.mobile_phone = self.address_id.mobile

    @api.onchange('company_id')
    def _onchange_company(self):
        address = self.company_id.partner_id.address_get(['default'])
        self.address_id = address['default'] if address else False

    @api.onchange('user_id')
    def _onchange_user(self):
        self.work_email = self.user_id.email
        self.name = self.user_id.name
        self.image = self.user_id.image

    @api.multi
    def write(self, vals):
        if 'name' in vals:
           vals['name_related'] = vals['name']
        return super(OeHealthPhysician, self).write(vals)

