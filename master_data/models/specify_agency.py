from odoo import fields, models,api,_
from datetime import date

from odoo.exceptions import ValidationError


class SpecifyAgent(models.Model):
    _name = 'specify.agent'
    _description = 'Specify Agent'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']

    name = fields.Char('Sequence',default='New',readonly=True)
    labor_id = fields.Many2one('labor.profile',required=True)
    passport_no = fields.Char(required=True)
    religion = fields.Selection([('muslim', 'Muslim'), ('christian', 'Christian'), ('jew', 'Jew'), ('other', 'Other')],'Religion')
    age = fields.Integer()
    state = fields.Selection([('draft', 'draft'),('available', 'Available'), ('selected', 'Selected'), ('done', 'done')], default='draft', track_visibility="onchange")
    request_date = fields.Date(default=date.today())
    available_date = fields.Date()
    select_date = fields.Date('Selection Date')
    employer = fields.Char()
    employer_mobile = fields.Char()
    agency = fields.Many2one('res.partner',domain=[('agency','=',True)])
    destination_city = fields.Char()
    visa_no = fields.Char()

    @api.multi
    def move_to_available(self):
        if not self.agency:
            raise ValidationError(_('you must enter agency'))
        self.labor_id.agency = self.agency.id
        self.labor_id.agency_code = self.id
        sequence = self.env['ir.sequence'].next_by_code('specify.agent')
        self.name = self.agency.short_code +'-'+ sequence
        self.state='available'
        self.available_date = date.today()

    @api.multi
    def select(self):
        self.state = 'selected'
        self.select_date = date.today()
        self.labor_id.specify_agency = 'selected'
        if self.labor_id.interpol_no and self.labor_id.after_medical_check == 'fit':
            self.env['labor.embassy'].create({
                'labor_id': self.labor_id.id,
                'passport_no': self.labor_id.passport_no,
                'interpol_no': self.labor_id.interpol_no,
                'big_medical': 'fit',
                'agency': self.agency.id,
                'employer': self.employer,
                'city': self.destination_city,
                'visa_no': self.visa_no,

            })
            self.env['labor.clearance'].create({
                'labor_id': self.labor_id.id,
                'passport_no': self.labor_id.passport_no,
                'gender': self.labor_id.gender,
                'job_title': self.labor_id.occupation,
                'name':self.labor_id.name,
                'contact': self.labor_id.phone,
                'lc1': self.labor_id.lc1.id,
                'lc2': self.labor_id.lc2.id,
                'lc3': self.labor_id.lc3.id,
                'district': self.labor_id.district.id,
                'agency': self.agency.id,
            })
            self.env['travel.company'].create({
                'labor_id': self.labor_id.id,
                'passport_no': self.labor_id.passport_no,
                'agency': self.agency.id,
                'agency_code': self.name,
            })



class MassAgency(models.TransientModel):
    _name = 'mass.agency'
    agency = fields.Many2one('res.partner',required=True)
    @api.multi
    def enter_agency(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for record in self.env['specify.agent'].browse(active_ids):
            record.agency = self.agency.id
            record.move_to_available()