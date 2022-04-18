# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, SUPERUSER_ID, fields, models, _


class OeHealthPatient(models.Model):
    _name = 'oeh.medical.patient'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _inherits = {
        'res.partner': 'partner_id',
    }
    _description = 'Medical Patient'



    SEX = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='cascade',
                                 help='Partner-related data of the patient')
    age = fields.Char(size=32, string='Age',
                      help="It shows the age of the patient in years(y), months(m) and days(d).\nIf the patient has died, the age shown is the age at time of death, the age corresponding to the date on the death certificate. It will show also \"deceased\" on the field")
    sex = fields.Selection(SEX, string='Sex', index=True)
    identification_code = fields.Char(string='Patient ID', size=256,
                                      help='Patient Identifier provided by the Health Center', readonly=True)
    address = fields.Char()
    occupation =fields.Char()
    country_id = fields.Many2one('res.country', string='Nationality')

    ssn = fields.Char(size=256, string='National ID')
    general_info = fields.Text(string='General Information', help="General information about the patient")
    Social = fields.Boolean("social media")
    Friend = fields.Boolean()
    T_V = fields.Boolean()
    Outdoor = fields.Boolean()
    Visita = fields.Boolean()
    invoice_count = fields.Integer(compute='_invoice_count', string="Invoices")
    service_count = fields.Integer(compute='_service_count',string="Services")
    app_count = fields.Integer(compute="_app_count", string="Appointments")
    appointment_id = fields.One2many('oeh.medical.appointment','patient')
    service_ids = fields.One2many('oeh.medical.service','patient_id',readonly=True)
    prescription_ids = fields.One2many('oeh.medical.prescriptions','patient_id', string='Prescriptions', readonly=True,)
    evaluation_ids = fields.One2many('oeh.medical.evaluation','patient_id',string='Evaluation',readonly=True)
    evaluation_name_ids = fields.One2many('clinic.evaluation','patient_id')
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        if name:
            actions = self.search(['|','|','|',('name', operator, name),('phone', operator, name),('identification_code', operator, name),('ssn', operator, name)] + args, limit=limit)
            return actions.name_get()
        return super(OeHealthPatient, self)._name_search(name, args=args, operator=operator, limit=limit)

    @api.multi
    def _app_count(self):
        oe_apps = self.env['oeh.medical.appointment']
        for pa in self:
            domain = [('patient', '=', pa.id)]
            app_ids = oe_apps.search(domain)
            print(app_ids, "***" * 10)
            apps = oe_apps.browse(app_ids)
            app_count = 0
            for ap in apps:
                app_count += 1
            pa.app_count = app_count
        return True

    @api.multi
    def _service_count(self):
        oe_serves = self.env['oeh.medical.service']
        for service in self:
            domain = [('patient_id', '=', service.id)]
            service.service_count = oe_serves.search_count(domain)
        return True

    @api.multi
    def _invoice_count(self):
        oe_invoice = self.env['account.invoice']
        for inv in self:
            invoice_ids = self.env['account.invoice'].search([('patient', '=', inv.id)])
            invoices = oe_invoice.browse(invoice_ids)
            invoice_count = 0
            for inv_id in invoices:
                invoice_count += 1
            inv.invoice_count = invoice_count
        return True

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('oeh.medical.patient')
        vals['identification_code'] = sequence
        vals['is_patient'] = True
        vals['customer'] = True
        health_patient = super(OeHealthPatient, self).create(vals)
        return health_patient


class OeHealthPatientPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _description = 'Partner'

    is_patient = fields.Boolean(string='Is Patient', help='Check if the party is a patient')


class AccountInvoicePatient(models.Model):
    _inherit = 'account.invoice'

    patient = fields.Many2one('oeh.medical.patient', string='Related Patient', help="Patient Name")

