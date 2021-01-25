from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError
from odoo.exceptions import Warning


class PartnerRelativesDegrees(models.Model):
    _name = 'partner.relative.degree'

    name = fields.Char(required=True)


class PartnerRelatives(models.Model):
    _name = 'partner.relatives'

    name = fields.Char(required=True)
    relatives_degree = fields.Selection([('father', 'Father'), ('mother', 'Mother'), ('next_of_kin', 'Next Of Kin')],required=True,string='R Degrees')
    phone = fields.Char()
    national_id = fields.Char(string='ID',size=14)
    lc1 = fields.Many2one('labor.village', string='LC1')
    lc2 = fields.Many2one('labor.parish',string='LC2')
    lc3 = fields.Many2one('labor.subcounty',string='LC3')
    lc4 = fields.Many2one('labor.county',string='LC4')
    district = fields.Many2one('labor.district',string='District')
    tribe = fields.Many2one('labor.tribe')
    date_of_birth = fields.Date('DOB')
    nationality = fields.Many2one('res.country')
    note = fields.Char()
    partner_id = fields.Many2one('res.partner')


class Partner(models.Model):
    _inherit = 'res.partner'
    _sql_constraints = [('short_code_uniq', 'unique(short_code)', 'Short Code must be unique!')]
    is_slave = fields.Boolean('House Maid')
    gender = fields.Selection([("Male","Male"),("Female","Female")],string="type")
    age = fields.Integer(compute='_compute_slave_age')
    broker = fields.Many2one("master.broker",string="Brokers")
    date_of_birth = fields.Date("Date of Birth")
    pre_medical_check = fields.Selection([('Fit', 'Fit'),('Unfit', 'Unfit')],default='Fit')
    reason = fields.Char()
    short_code = fields.Char()
    relative_ids = fields.One2many('partner.relatives','partner_id')
    vendor_type = fields.Selection([('agent','Agent'),('passport_broker','Passport Broker'),('passport_placing_issue','Passport Placing Issue'),('interpol_broker','Interpol Broker'),('gcc','Gcc'),('hospital','Hospital'),('training','Training Center')])
    agency = fields.Boolean()
    agency_cost = fields.Float(track_visibility="onchange")
    cost = fields.Float(track_visibility="onchange")

    @api.constrains('cost')
    def constrains_cost(self):
        if self.vendor_type in ('passport_broker','interpol_broker','passport_placing_issue','hospital') and self.cost <= 0:
            raise ValidationError(_('You must enter Cost.'))



    @api.depends('date_of_birth')
    def _compute_slave_age(self):

        current_dt = date.today()
        for rec in self:
            if rec.date_of_birth:
                start = rec.date_of_birth
                age_calc = ((current_dt - start).days / 365)
                # Age should be greater than 0
                if age_calc > 21:
                    rec.age = age_calc
                else :
                    raise ValidationError(_('Not Enough reserved Qty.'))