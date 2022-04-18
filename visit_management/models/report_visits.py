from odoo import fields, api, models, _
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, date
from dateutil.relativedelta import relativedelta


class EmployeeServicesType(models.Model):
    _name = 'employee.service.type'

    name = fields.Char()


class EmployeeVisitsReport(models.TransientModel):
    _name = "employee.visits.report"
    # _rec_name = "employee_id"

    def _get_report_name(self):
        return _('visits Management')

    # employee_id = fields.Many2one('hr.employee')
    # service_type = fields.Many2one('employee.service.type', string="Service")
    start_date = fields.Date(string="Date From", compute="get_start_end_date", store=True)
    end_date = fields.Date(string="Date To", compute="get_start_end_date", store=True)
    month = fields.Selection([('1', 'January'),
                              ('2', 'February'),
                              ('3', 'March'),
                              ('4', 'April'),
                              ('5', 'May'),
                              ('6', 'June'),
                              ('7', 'July'),
                              ('8', 'August'),
                              ('9', 'September'),
                              ('10', 'October'),
                              ('11', 'November'),
                              ('12', 'December'),
                              ], default="1", required=True)

    @api.depends('month')
    def get_start_end_date(self):
        for rec in self:
            if rec.month:
                rec.start_date = date.today().replace(month=int(rec.month), day=1)
                rec.end_date = (rec.start_date + relativedelta(months=1, days=-1))


    def print_visits_report(self):
        print("Visits Report")
        data = {
            'ids': self.ids,
            'model': 'customer.visits',
            'form': {
                # 'employee_name': self.employee_id.name,
                'date_start': self.start_date,
                'date_end': self.end_date,
            }, }
        docs = []
        class_ids = self.env['visit.class'].search([])
        for class_id in class_ids:
            visit_ids = self.env['customer.visit'].sudo().search_count(
                [('start_date', '>=', fields.Date.to_string(self.start_date)),
                 ('start_date', '<=', fields.Date.to_string(self.end_date)),('class_id','=',class_id.id)])
            if visit_ids:
                coverage_plan = round(100*visit_ids/class_id.count)
                print(visit_ids,"class", class_id.name, "count", class_id.count,)
                visit_done = self.env['customer.visit'].sudo().search_count(
                    [('start_date', '>=', fields.Date.to_string(self.start_date)),
                     ('start_date', '<=', fields.Date.to_string(self.end_date)), ('class_id', '=', class_id.id),
                     ('state', '=', 'Done')])
                coverage_rate_plan = round(100*visit_done/class_id.count)
                coverage_rate_done = round(100*visit_done/visit_ids, 2)

                if visit_done:
                    docs.append({"class": class_id.name, "class_visits": class_id.count,
                         "plan_visits": visit_ids,"coverage_plan":coverage_plan,"frequency_plan":100,
                             'visit_done':visit_done,'coverage_rate_plan':coverage_rate_plan,
                             "coverage_rate_done":coverage_rate_done,
                             "frequency_done":100,})
                else:
                    docs.append({"class": class_id.name, "class_visits": class_id.count,
                                 "plan_visits": visit_ids, "coverage_plan": coverage_plan, "frequency_plan": 100,
                                 'visit_done': visit_done, 'coverage_rate_plan': coverage_rate_plan,
                                 "coverage_rate_done": coverage_rate_done,
                                 "frequency_done": 0, })
            else:
                docs.append({"class": class_id.name, "class_visits": class_id.count,
                             "plan_visits": 0, "coverage_plan": 0, "frequency_plan": 0,
                             'visit_done': 0, 'coverage_rate_plan': 0,
                             "coverage_rate_done": 0,
                             "frequency_done": 0, })
        data['docs'] = docs
        print("visits docs", "=======================", data["docs"])
        customer_visits = []
        for class_id in class_ids:
            customers = self.env['res.partner'].search([('class_id','=',class_id.id)])
            customer_visit_list = []
            for customer in customers:
                customer_plan_visits = self.env['customer.visit'].sudo().search_count(
                [('start_date', '>=', fields.Date.to_string(self.start_date)),
                 ('start_date', '<=', fields.Date.to_string(self.end_date)),
                 ('customer_id', '=', customer.id)])

                if customer_plan_visits:
                    coverage_plan = round(100 * customer_plan_visits / customer.class_id.count, 2)
                    print("customer.class_id.name",customer.class_id.name)
                    print(customer_plan_visits, "class", customer.class_id.name, "count", customer.class_id.count)
                    customer_done = self.env['customer.visit'].sudo().search_count(
                        [('start_date', '>=', fields.Date.to_string(self.start_date)),
                         ('start_date', '<=', fields.Date.to_string(self.end_date)),
                         ('customer_id', '=', customer.id),('state', '=', 'Done')])
                    if customer_done:
                        frequency_class_visit = round(100 * customer_plan_visits / customer.class_id.count, 2)
                        coverage_rate_done_class = round(100 * customer_done / customer.class_id.count, 2)
                        coverage_rate_done_plan = round(100 * customer_done / customer_plan_visits, 2)
                        customer_visit_list.append({"doctor": customer.name, "class": customer.class_id.name,
                                                    "class_visits": customer.class_id.count,
                                                    "plan_visits": customer_plan_visits, "coverage_plan": coverage_plan,
                                                    "frequency_plan": 100, 'customer_done': customer_done,
                                                    "coverage_rate_done_class": coverage_rate_done_class,
                                                    "coverage_rate_done_plan": coverage_rate_done_plan, "frequency_done": 100, })
                    else:
                        customer_visit_list.append({"doctor": customer.name, "class": customer.class_id.name,
                                                    "class_visits": customer.class_id.count,
                                                    "plan_visits": customer_plan_visits, "coverage_plan": coverage_plan,
                                                    "frequency_plan": 100, 'customer_done': customer_done,
                                                    "coverage_rate_done_class": 0,
                                                    "coverage_rate_done_plan": 0, "frequency_done": 0, })
                else:
                    customer_visit_list.append({"doctor": customer.name, "class": customer.class_id.name,
                                                "class_visits": customer.class_id.count,
                                                "plan_visits": 0, "coverage_plan": 0,
                                                "frequency_plan": 0, 'customer_done': 0,
                                                "coverage_rate_done_class": 0,
                                                "coverage_rate_done_plan": 0, "frequency_done": 0, })
            customer_visits.append({"class": class_id.name, "visits":customer_visit_list})
        data['customers'] = customer_visits
        return self.env.ref('visit_management.visit_management_report_action').report_action(self, data=data)


class ReportVisitsPlanForEmployee(models.AbstractModel):
    """Abstract Model for report template.
    for `_name` model, please use `report.` as prefix then add `module_name.report_name`.
    """
    _name = 'report.visit_management.visit_management_report'

    def _get_report_values(self, docids, data=None):
        docs = data['docs']
        print(data['form']['date_start'])
        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': data['form']['date_start'],
            'date_end': data['form']['date_end'],
            'docs': docs,
            'customers': data['customers'],
        }

