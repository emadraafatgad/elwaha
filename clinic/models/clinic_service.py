from odoo import api, fields, models, exceptions ,_
from datetime import date
from odoo.exceptions import ValidationError, UserError


class ClinicService(models.Model):
    _name = 'oeh.medical.service'
    _inherit = ['mail.thread']
    _description = "it's service Description"

    Sessions_STATUS = [
        ('New','New'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Canceled', 'Canceled'), ]

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

    name = fields.Char(string='Session #', readonly=True, size=64, default=lambda *a: '/')
    state = fields.Selection(Sessions_STATUS, track_visibility='onchange', string='State',
                             readonly=True, default=lambda *a: 'New')
    service_line_id = fields.Many2one('oeh.medical.service.line',string="Session Name",
                                      domain="[('service_type_id','=',service_type_id)]")
    service_type_id = fields.Many2one('oeh.medical.service.type',string="Category")
    patient_id = fields.Many2one('oeh.medical.patient', required=True)
    doctor_id = fields.Many2one('oeh.medical.physician',track_visibility='onchange',string="Doctor",required=True)
    assist_doctor = fields.Many2one('oeh.medical.physician', string='Assistant Doctor', help="Current primary care",
                                    domain=[],)
    s_discount = fields.Float(string="Session Discount" ,placeholder="Discount If There is an Offer")
    total_cost = fields.Integer(string="Total Cost", compute='calc_session_price' ,track_visibility='onchange',store=True)
    cost = fields.Integer(related='service_line_id.session_cost',string="Session Cost",store=True)
    completed_sessions = fields.Integer(track_visibility='onchange')
    appointment_id = fields.Many2one('oeh.medical.appointment')
    note = fields.Text()
    evaluation_ids = fields.One2many('oeh.medical.evaluation','service_id')
    service_date = fields.Date(string="Session start Date",default=fields.Date.context_today, required=True,)
    next_session = fields.Date(track_visibility='onchange',)
    prescription_ids = fields.One2many('oeh.medical.prescriptions','service_id')
    medicine_value_ids = fields.One2many('oeh.medical.medicine.value', 'service_id')
    service_package_id = fields.Many2one('clinic.service.package',string="Sessions Package")
    clinic_type = fields.Selection([('nutrition', 'Nutrition clinic'), ('beauty', 'Beauty Clinic')], default="beauty")
    is_package = fields.Boolean("Is Package ?")
    package_sessions = fields.Integer("Sessions Count",default=1,placeholder='Sessions Count in Package')
    package_price = fields.Integer("Package Price",compute='_get_package_price', readonly=False)
    vip_discount = fields.Integer()
    price_after = fields.Integer()
    paid_amount = fields.Integer()
    due_amount = fields.Integer()
    clinic_id = fields.Many2one('res.company', 'Clinic', default=lambda self: self.env.user.company_id, ondelete='cascade')
    stage_id = fields.Many2one('service.stage', string='Stage', ondelete='restrict', track_visibility='onchange',
                               default=lambda self: self._default_stage_id(), index=True)
    color = fields.Integer('Color Index', default=0)

    def _default_stage_id(self):
        return self.env['service.stage'].search([('fold', '=', False)], limit=1).id

    @api.multi
    def _app_amount(self):
        oe_invoice = self.env['account.invoice']
        for inv in self:
            invoice_pbj = oe_invoice.search([('service_id', '=', inv.id)])
            print(invoice_pbj,"OBJ")
            if invoice_pbj.state == "draft":
                print(invoice_pbj.amount_total)
                inv.due_amount = invoice_pbj.amount_total
            elif invoice_pbj != "draft":
                print(invoice_pbj.residual, "============")
                inv.due_amount = invoice_pbj.residual
            else :
                print("No invoice")
        return True

    @api.multi
    def _default_account(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)
        return journal.default_credit_account_id.id

    @api.depends('s_discount','cost')
    def calc_session_price(self):
        self.total_cost = self.cost * (1 - self.s_discount/100)

    def _add_session_invoice(self):
        invoice_obj = self.env["account.invoice"]
        invoice_line_obj = self.env["account.invoice.line"]
        # app_conf = self.env['oeh.medical.config'].search([], limit=1)
        # print(app_conf.consultancy_price)
        inv_ids = []
        for acc in self:
            # Create Invoice
            print("NEW"  if acc.state == "New" else "NOT", acc.state ,type(acc.state))
            if acc.patient_id and acc.state == 'New':
                curr_invoice = {
                    'partner_id': acc.patient_id.partner_id.id,
                    'patient': acc.patient_id.id,
                    'account_id': acc.patient_id.partner_id.property_account_receivable_id.id,
                    'state': 'draft',
                    'type': 'out_invoice',
                    # 'date_invoice': acc.appointment_date,
                    'origin': acc.name,
                }
                inv_ids = invoice_obj.create(curr_invoice)
                inv_id = inv_ids.id

                if inv_ids:
                    prd_account_id = self._default_account()
                    # Create Invoice line
                    curr_invoice_line = {
                        'name': "Consultancy invoice for " + acc.service_line_id.name if not acc.is_package else "it is package of "+ str(acc.package_sessions) +  " "+ acc.service_line_id.name,
                        'price_unit': acc.price_after if acc.is_package==True and acc.price_after else acc.total_cost,
                        # 'invoice_line_tax_ids': [(6, 0, [app_conf.visita.id])],
                        'quantity': 1,
                        'account_id': prd_account_id,
                        'invoice_id': inv_id,
                    }
                    inv_line_ids = invoice_line_obj.create(curr_invoice_line)
                # inv_ids.compute_taxes()


        return True

    @api.onchange('vip_discount','package_price')
    def _compute_price(self):
        for record in self:
            record.price_after = record.package_price*(1-record.vip_discount/100)
            print(record.price_after,"price after")

    @api.depends('is_package','package_sessions')
    def _get_package_price(self):
        for rec in self:
            print("/////////////", rec.package_sessions * rec.cost)
            rec.package_price = rec.package_sessions * rec.cost

    # @api.onchange('service_line_id')
    def get_service_line_medicine(self,service_id):
        medicine_value_obj = self.env['oeh.medical.medicine.value']
        print("in medicine value")
        val_ids = []
        for rec in self:
            for line in rec.service_line_id.medicine_value_ids:
                print(line,line.medicine_id.id,rec.id,line.quantity,line.unit_price,line.total_price,)
                medicine_ids = medicine_value_obj.create({
                    'medicine_id':line.medicine_id.id,
                    'service_id':service_id,
                    'quantity':line.quantity,
                    'unit_price':line.unit_price,
                    'total_price':line.total_price,
                })
                val_ids.append(medicine_ids.id)
            print(val_ids)
            # return  val_ids
            rec.medicine_value_ids = [(6,0,val_ids)]
            print(rec.medicine_value_ids,"====------------------------------====")

    @api.model
    def create(self, vals):
        sequence = self.env['ir.sequence'].next_by_code('oeh.medical.service')
        vals['name'] = sequence
        clinic_service = super(ClinicService, self).create(vals)
        val_ids = clinic_service.get_service_line_medicine(clinic_service.id)
        return clinic_service
        # vals['medicine_value_ids'] = [(6, 0, val_ids)]

    def start_session_service(self):
        print("start")
        if self.is_package == True:
            self.completed_sessions += 1
            self.state = 'In Progress'
        elif self.is_package != True:
            self.state = 'Completed'
        # self.move_medicine_to_inventory()
        self.send_stock_req()
        self.create_dr_payment_line()
        self._add_session_invoice()

    def create_dr_payment_line(self):
        charge_line = self.env['amount.dr.percentage.line']
        charge_line.create({
            'doctor':self.doctor_id.id,
            'service_id': self.service_line_id.id,
            'work_date':self.service_date,
            'amount': self.total_cost,
        })
        print(charge_line)

    @api.multi
    def move_medicine_to_inventory(self):
        print("INvENtory")
        for rec in self:
            stock_move_without_package = self.env['stock.move']
            inventory_transfers_obj = self.env['stock.picking']
            transfer_operation_obj = self.env['stock.picking.type'].search([('code','=','outgoing'),('active','=',True)],limit=1)
            print(transfer_operation_obj,"Transfer_operation_obj")
            inventory_transfers_id = inventory_transfers_obj.create({'partner_id':rec.patient_id.partner_id.id,
                                                                    'picking_type_id':transfer_operation_obj.id,
                                                                     'location_dest_id':transfer_operation_obj.default_location_dest_id.id,
                                                                     'location_id':transfer_operation_obj.default_location_src_id.id})
            print(inventory_transfers_obj,inventory_transfers_id,"=======================id")
            stock_moves_ids =[]
            for medicine in rec.service_line_id.medicine_value_ids:
                stock_move_without_package.create({'product_id':medicine.medicine_id.id,'product_uom_qty':medicine.quantity,'picking_id':rec.id})

    def send_stock_req(self):
        operation_type_id, location_id, location_dst_id = self.get_inventory_locations()
        print("i am in stock ")
        partner_id = self.env['res.partner'].search([('name', 'ilike', self.doctor_id.name)],limit=1)
        print("before create",operation_type_id,location_id, location_dst_id)

        picking_out = self.env['stock.picking'].create({
            'partner_id': self.patient_id.partner_id.id,
            'state': 'draft',
            'origin':self.name,
            'picking_type_id': operation_type_id,
            'location_id': location_id,
            'location_dest_id': location_dst_id,
            'move_lines': [],
        })
        print("after create",picking_out)
        move_list = []
        for line in self.medicine_value_ids:
            move_line_id = self.env['stock.move'].create({
                'name': line.medicine_id.product_id.name,
                'product_id': line.medicine_id.product_id.id,
                'product_uom_qty': line.quantity,
                'product_uom':line.medicine_id.product_id.uom_id.id,
                'picking_id': picking_out.id,
                'location_id': location_id,
                'location_dest_id': location_dst_id,
            })
            move_line_id.quantity_done = line.quantity
            move_list.append(move_line_id.id)
        picking_out.stock_move_without_package = [(6,0,move_list)]
        print(picking_out.stock_move_without_package)
        picking_out.action_confirm()
        picking_out.action_assign()
        picking_out.button_validate()

    def get_inventory_locations(self):
        user_company =  self.env.user.company_id.id
        print(user_company,self.env.user.company_id,self.env.user.company_id.name)
        company_partner = self.env['res.company'].search([('id','=',user_company)],limit=1)
        print(company_partner,"company_partner")
        warehouse_id = self.env['stock.warehouse'].search([('company_id','=',company_partner.id)])
        print("wearwhouse id ", warehouse_id)
        operation_type_ids = self.env['stock.picking.type'].search([('name', '=', 'Delivery Orders'),('warehouse_id','=',warehouse_id.id)])
        operation_id = self.env['stock.picking.type']
        location_id =0
        location_dst_id=0
        operation_type_id = 0
        for op in operation_type_ids:
            print(op.id)
            print(op.name)
            operation_type_id = op.id
            if op.default_location_src_id:
                location_id = op.default_location_src_id.id
            else:
                raise ValidationError(_('you should add default  Source Location'))
            if op.default_location_dest_id.id:
                location_dst_id = op.default_location_dest_id.id
            else :
                raise ValidationError(_('you should add default  destination Location'))
        if location_dst_id and location_id > 0:
            return operation_type_id , location_id ,location_dst_id

    def complete_service(self):
        print("Completed")
        self.state = 'Completed'

    def cancel_service(self):
        print("Canceled")
        self.state = 'Canceled'


class AppointmentSessions(models.Model):
    _inherit = "oeh.medical.appointment"

    service_count = fields.Integer(compute='_service_count', string="Sessions")

    @api.depends('patient')
    def _service_count(self):
        oe_serves = self.env['oeh.medical.service']
        for service in self:
            domain = [('patient_id', '=', service.patient.id)]
            service.service_count = oe_serves.search_count(domain)
            print(service.service_count,"c====s ")
            # print(service.app_count)
        return True


class ClinicServiceStage(models.Model):
    _name = 'service.stage'
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

    state = fields.Selection(APPOINTMENT_STATUS,  string='State',
                             default=lambda *a: 'Scheduled')


class AccountInvoiceAppointment(models.Model):
    _inherit = 'account.invoice'

    service_id = fields.Many2one('oeh.medical.service', string='Related Session', help="Session ")
