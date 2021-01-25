from odoo import models, fields, api, tools, exceptions, _
from odoo.exceptions import Warning, UserError


class CustomerVisits(models.Model):
    _name = 'customer.visit'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char()
    active = fields.Boolean(default=True)
    title = fields.Char(string="Description",required=True,track_visibility='onchange',)
    customer_id = fields.Many2one('res.partner',required=True,string="Doctor", domain="[('customer','=',True)]")
    class_id = fields.Many2one(related="customer_id.class_id",store=True)
    class_count = fields.Integer(related='class_id.count',store=True)
    class_remain = fields.Integer(readonly=True,store=True)
    employee_id = fields.Many2one('hr.employee',required=True,track_visibility='onchange')
    state = fields.Selection([('New','New'),('Postpone','Postpone'),('Done','Completed'),('Canceled','Cancel')],
                             default='New',track_visibility='onchange',)

    start_date = fields.Datetime(string="Date",track_visibility='onchange',required=True)
    period = fields.Float(track_visibility='onchange')
    end_date = fields.Datetime()
    note = fields.Text()
    visit_id = fields.Many2one('visit.plan')
    document = fields.Binary("Attachments", attachment=True)
    document_filename = fields.Char(
        string='Attachments', )

    def cal_remaining_qty(self):
        for line in self:
            visits_count = self.env['customer.visit'].search_count([('class_id','=',line .class_id.id),('visit_id','=',line.visit_id.id),('employee_id','=',line.employee_id.id)])
            class_remain = line .class_count - visits_count
            print(visits_count,"vusisa acouas",line .visit_id)
        return class_remain

    @api.model
    def create(self, vals):
        name = self.env['ir.sequence'].next_by_code('customer.visit')

        vals.update({
            'name': name
        })
        res = super(CustomerVisits, self).create(vals)
        visits_count = self.env['customer.visit'].search_count(
            [('class_id','=',res.class_id.id),
                ('visit_id', '=', vals['visit_id']),
             ('employee_id', '=', vals['employee_id'])])
        print(visits_count,"visits count")
        class_remain = res.class_count - visits_count -1
        if class_remain < 0:
            raise Warning(_("This class visits plan is completed"))
        else:
            res.class_remain = class_remain
        return res

    @api.multi
    def cancel_visit(self):
        self.state="Canceled"


    @api.multi
    def confirm_visit(self):
        self.state = "Done"

    @api.multi
    def postpone_visit(self):
        self.state = "Postpone"


class VisitsClass(models.Model):
    _inherit = 'visit.plan'

    customer_visit_ids = fields.One2many('customer.visit','visit_id')
    total_visits = fields.Float(string="Coverage Rate - plan", compute="cover_rate",store=True)
    coverage = fields.Float(compute="cover_rate",string="Coverage Rate - Done Visits",store=True)

    @api.depends('customer_visit_ids.state','count')
    def cover_rate(self):
        for rec in self:
            sum = 0
            done_sum =0
            for line in rec.customer_visit_ids:
                if line.state == 'Done':
                    done_sum= done_sum + 1
                    print(done_sum,"Done")
                sum = sum + 1
            print(sum,"sum",rec.count,"count")
            # if sum > rec.count:
            #     raise Warning(_("you cant create Orders More then planed"))
            #     rec.total_visits = 100*sum/ rec.count
            if sum :
                rec.coverage = 100*done_sum/sum