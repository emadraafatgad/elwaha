from odoo import fields, api, models


class ClinicServicePackage(models.Model):
    _name = "clinic.service.package"

    name = fields.Char()
    patient_id = fields.Many2one('oeh.medical.patient')
    start_date = fields.Date()
    next_date = fields.Date()
    # service_line_ids = fields.Many2many('oeh.medical.service.line',)
    services_ids = fields.One2many('oeh.medical.service','package_id')
    package_line_id =  fields.Many2one('service.package.line')
    service_package_line_ids = fields.One2many("clinic.service.package.line",'package_id')

    @api.onchange('package_line_id')
    def service_package_line(self):
        for rec in self:
            line_id = []
            for line in rec.package_line_id.service_package_line_ids:
                line_id.append(line.id)
            rec.service_package_line_ids =[(6,0,line_id)]


class ClinicServicePackageLine(models.Model):
    _name = "service.package.line"

    name = fields.Char()
    service_package_line_ids = fields.One2many("clinic.service.package.line",'package_line_id',string="Sessions List")
    package_price = fields.Integer(compute='service_package_total_price',store=1)
    note = fields.Text()

    @api.depends('service_package_line_ids')
    def service_package_total_price(self):
        for line in self.service_package_line_ids:
            self.package_price += line.total_price


class ClinicServiceLines(models.Model):
    _name = "clinic.service.package.line"

    service_line_ids = fields.Many2one('oeh.medical.service.line', )
    count = fields.Integer(default=1)
    unit_price = fields.Integer()
    total_price = fields.Integer(compute='service_total_price',store=True,readonly=False)
    package_id = fields.Many2one('clinic.service.package',)
    package_line_id = fields.Many2one('service.package.line')

    @api.depends('count','unit_price')
    def service_total_price(self):
        print("package line price")
        for rec in self:
            rec.update({'total_price':rec.unit_price*rec.count})
            print(rec.unit_price,rec.count)


class ClinicService(models.Model):
    _inherit = 'oeh.medical.service'

    package_id = fields.Many2one('clinic.service.package',)