from odoo import fields ,models, _, api


class Employee(models.Model):
    _inherit = 'hr.employee'

    classera_id = fields.Integer('Classera ID',copied=True)

    _sql_constraints = [
        ('classera_id_uniq', 'UNIQUE (classera_id)', 'You can not have two records with the same Classera ID !')
    ]


class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_employee_payslip(self, classera_id):
        """ Definition that gets the children information and there payments takes parent_id """
        print('paysllip called')
        employee_obj = self.env['hr.employee'].search([('classera_id', '=', classera_id)], limit=1)[0]
        if employee_obj:
            employee_id = employee_obj.id
            payslip_list = []
            payslip_objs = self.env['hr.payslip'].search([('employee_id', '=', employee_id)])
            for payslip in payslip_objs:
                payslip_id = self.env['hr.payslip'].search_read([('id', '=', payslip.id)])
                print(payslip_id)
                print("===========***************-----------")
                payslip_lines = []
                for line in payslip.line_ids :
                    payslip_lines.append({"name": line.name, "total": line.total})
                payslip_id[0]['line_ids'] = payslip_lines
                payslip_list.append(payslip_id)
            try:
                return payslip_list
            except:
                return {'message': "Cant Get Employee With it"}

