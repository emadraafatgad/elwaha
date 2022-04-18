from odoo import fields, api, models


class ClinicServicePackageId(models.Model):
    _inherit = "oeh.medical.service"

    package_id = fields.Many2one('clinic.service.package', ondelete='cascade')


class ClinicServicePackageLine(models.Model):
    _name = "service.package.line"

    name = fields.Char()
    service_package_line_ids = fields.One2many("clinic.service.package.line",'package_line_id')
    package_price = fields.Integer()
    note = fields.Text()

    @api.depends('service_package_line_ids')
    def service_package_total_price(self):
        self.package_price = 0
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

