import datetime
from datetime import date, datetime
from datetime import timedelta
import logging
import pytz
from requests import help

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.translate import _


class OeHealthAppointment(models.Model):
    _name = 'oeh.medical.appointment'
    _description = 'Appointment'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _order = "queue asc"



    # Automatically detect logged in physician
    @api.multi
    def _get_physician(self):
        """Return default physician value"""
        therapist_obj = self.env['oeh.medical.physician']
        domain = [('oeh_user_id', '=', self.env.uid)]
        user_ids = therapist_obj.search(domain, limit=1)
        if user_ids:
            return user_ids.id or False
        else:
            return False

    name = fields.Char(string='Appointment #', readonly=True, size=64, default=lambda *a: '#')
    patient = fields.Many2one('oeh.medical.patient', string='Patient', help="Patient Name", required=True,)
    doctor = fields.Many2one('oeh.medical.physician', string='Doctor', help="Current primary care", domain=[],
                             required=True, )
    assist_doctor = fields.Many2one('oeh.medical.physician', string='Assistant Doctor', help="Current primary care",
                                    domain=[] )
    queue = fields.Char(string="queue", track_visibility='onchange', readonly=True)
    appointment_date = fields.Date(string='Appointment Date', required=True,
                                   default=date.today())
    # appointment_date_str = fields.Char(string='Appointment Date')
    arrive_time = fields.Char(string='Arrive Time', track_visibility='onchange', readonly=True, )
    clinic = fields.Many2one('res.company', 'Clinic', default=lambda self: self.env.user.company_id, ondelete='cascade')
    # states = {'Scheduled': [('readonly', False)]}
    comments = fields.Text(string='Comments')
    app_source = fields.Selection([
        ('VISITA', 'VISITA'), ('Personal', 'Personal')
    ], string="Source", default="Personal")

    app_type = fields.Selection([
        ('New', 'New'), ('First', 'First Follow Up'), ('Second', 'Second Follow up'),('session','Session')],
        string="Type", track_visibility='onchange',  default="New")

    APPOINTMENT_STATUS = [
        ('Scheduled', 'Scheduled'),
        ('Arrived', 'Arrived'),
        ('Invoiced', 'Invoiced'),
        ('Completed', 'Completed'),
        ('Canceled', 'Canceled'),
    ]

    state = fields.Selection(APPOINTMENT_STATUS, track_visibility='onchange', string='State',
                             readonly=True, default='Scheduled')
    # appointment_day = fields.Char(string='Appointment Day', compute='get_appointment_day', )

    service_ids = fields.One2many('oeh.medical.service', 'appointment_id')
    evaluation_ids = fields.One2many('oeh.medical.evaluation', 'appointment_id')
    evaluation_name_ids = fields.Many2many('clinic.evaluation')
    prescription_ids = fields.One2many('oeh.medical.prescriptions', 'appointment_id')
    stage_id = fields.Many2one('appointment.stage', string='Stage', ondelete='restrict', track_visibility='onchange',
                               default=lambda self: self._default_stage_id(), index=True)
    color = fields.Integer('Color Index', default=0)
    clinic_type = fields.Selection([('nutrition','Nutrition clinic'),('beauty','Beauty Clinic')],default="beauty")
    invoice_count = fields.Integer(compute='_invoice_count', string="Invoices")
    app_count = fields.Integer(compute="_app_count", string="Appointments")
    app_amount = fields.Float(compute='_app_amount', string="Due Amount", )
    discount = fields.Float(placeholder="Discount %")

    # @api.depends('stage_id')
    @api.multi
    def _app_amount(self):
        oe_invoice = self.env['account.invoice']
        for inv in self:
            invoice_pbj = oe_invoice.search([('appointment_id', '=', inv.id)])
            print(invoice_pbj,"OBJ")
            if invoice_pbj.state == "draft":
                print(invoice_pbj.amount_total)
                inv.app_amount = invoice_pbj.amount_total
            elif invoice_pbj != "draft":
                print(invoice_pbj.residual, "============")
                inv.app_amount = invoice_pbj.residual
            else :
                print("No invoice")
        return True

    @api.model
    def _onchange_stage_id_values(self, stage_id):
        """ returns the new values when stage_id has changed """
        if not stage_id:
            return {}
        stage = self.env['appointment.stage'].browse(stage_id)
        if stage.state:
            print("-------------", stage.state)
            return {'state': stage.state}
        return {}

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        values = self._onchange_stage_id_values(self.stage_id.id)
        self.update(values)

    @api.multi
    def _app_count(self):
        oe_apps = self.env['oeh.medical.appointment']
        for pa in self:
            domain = [('patient', '=', pa.patient.id)]
            pa.app_count = oe_apps.search_count(domain)
        return True

    @api.depends('patient')
    def _invoice_count(self):
        oe_invoice = self.env['account.invoice']
        for inv in self:
            domain = [('patient', '=', inv.patient.id)]
            total_invoices = oe_invoice.search(domain)
            due = 0
            print(due)
            for invoice in total_invoices:
                due += invoice.residual
                print(due)
            inv.invoice_count = due
            # inv.invoice_count = oe_invoice.search_count([('patient', '=', inv.patient.id)])
        return True


    def set_arrived_state(self):
        print("set arrive")
        odoo_date = fields.Datetime.to_string(datetime.now())
        print(odoo_date, type(odoo_date))
        date = odoo_date.split(' ')
        print(date)
        time = date[1].split('-')
        print(time[0], "time")
        self.write({'arrive_time': time[0],'state':"Arrived"})
        self.add_to_queue(date[0])
        print("i am not")
        return True

    def add_to_queue(self, odoo_date):
        print(odoo_date, "odoo_date")
        print(self.appointment_date, "appointment_date")
        appointment_ids = self.env['oeh.medical.appointment'].search([('appointment_date', 'ilike', odoo_date)],
                                                                     order='queue desc')
        print(appointment_ids, "ddddddd")
        if appointment_ids:
            for appointment_id in appointment_ids:
                if appointment_id and appointment_id.queue:
                    print(appointment_id.name, appointment_id.id)
                    self.queue = int(appointment_id.queue) + 1
                    break
                else:
                    self.queue = 1

        else:
            self.queue = 1

    @api.multi
    def set_to_completed(self):
        return self.write({'state': 'Completed'})

    @api.multi
    def set_to_cancel(self):
        print("state Canceld")
        return self.write({'state': 'Canceled'})

    # if vals.get('doctor') and vals.get('appointment_date'):
    #     self.check_physician_availability(vals.get('doctor'),vals.get('appointment_date'))

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('oeh.medical.appointment')
        vals['name'] = sequence
        health_appointment = super(OeHealthAppointment, self).create(vals)
        return health_appointment


    @api.multi
    def _default_account(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        return journal.default_credit_account_id.id

    def action_appointment_invoice_create(self):
        # self.state = "Invoiced"
        invoice_obj = self.env["account.invoice"]
        invoice_line_obj = self.env["account.invoice.line"]
        app_conf = self.env['oeh.medical.config'].search([], limit=1)
        print(self.doctor.consultancy_price)
        inv_ids = []

        for acc in self:
            # Create Invoice
            if acc.patient:
                curr_invoice = {
                    'partner_id': acc.patient.partner_id.id,
                    'patient': acc.patient.id,
                    'appointment_id': acc.id,
                    'account_id': acc.patient.partner_id.property_account_receivable_id.id,
                    'state': 'draft',
                    'type': 'out_invoice',
                    'date_invoice': acc.appointment_date,
                    'origin': acc.name,
                }

                inv_ids = invoice_obj.create(curr_invoice)
                inv_id = inv_ids.id
                print(acc.doctor.consultancy_price,"**************")
                if inv_ids:
                    prd_account_id = self._default_account()
                    # Create Invoice line
                    curr_invoice_line = {
                        'name': "Consultancy invoice for " + acc.patient.name,
                        'price_unit': acc.doctor.consultancy_price * (1-acc.discount/100),
                        'invoice_line_tax_ids':[(6,0,[app_conf.visita.id])],
                        'quantity': 1,
                        'account_id': prd_account_id,
                        'invoice_id': inv_id,
                    }
                    inv_line_ids = invoice_line_obj.create(curr_invoice_line)
                inv_ids.compute_taxes()
                inv_ids.action_invoice_open()
            acc._app_amount()
            self.write({'state': 'Invoiced'})
        return True

    @api.onchange('patient')
    def get_patient_history(self):
        if self.patient:
            self.evaluation_name_ids = self.env['clinic.evaluation'].search([('patient_id', '=', self.patient.id)]).ids

    def _default_stage_id(self):
        return self.env['appointment.stage'].search([('fold', '=', False)], limit=1).id


class OeHealthClinic(models.Model):
    _name = 'oeh.medical.clinic'

    name = fields.Char("Clinic")


class ClinicAppointmentStage(models.Model):
    _name = 'appointment.stage'
    _rec_name = 'name'
    _order = "sequence, name, id"

    name = fields.Char()
    fold = fields.Boolean('Folded in Pipeline',
                          help='This stage is folded in the kanban view when there are no records in that stage to display.')
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    APPOINTMENT_STATUS = [
        ('Scheduled', 'Scheduled'),
        ('Arrived', 'Arrived'),
        ('Invoiced', 'Invoiced'),
        ('Completed', 'Completed'),
        ('Canceled', 'Canceled'), ]

    state = fields.Selection(APPOINTMENT_STATUS, string='State',default=lambda *a: 'Scheduled')


class AccountInvoiceAppointment(models.Model):
    _inherit = 'account.invoice'

    appointment_id = fields.Many2one('oeh.medical.appointment', string='Related Appointment', help="Patient Name")
