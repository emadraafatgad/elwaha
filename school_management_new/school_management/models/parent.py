# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api


class ParentRelation(models.Model):
    """Defining a Parent relation with child"""
    _name = "parent.relation"
    _description = "Parent-child relation information"

    name = fields.Char("Relation name", required=True)


class ResPartner(models.Model):
    """ Defining a Teacher information """
    _inherit = 'res.partner'

    is_parent = fields.Boolean()
    parent_relation_id = fields.Many2one("parent.relation")
    is_student = fields.Boolean()
    classera_id = fields.Integer('Classera ID', stored=True, copied=True)

    _sql_constraints = [
        ('classera_id_uniq', 'UNIQUE (classera_id)', 'You can not have two records with the same Classera ID !')
    ]

    @api.onchange('is_parent')
    def get_company_type(self):
        if self.is_parent:
            self.company_type = 'company'
        else:
            self.company_type = 'person'

    # def get_students(self):
    #     print("Call Function")
    #     if self.is_parent:
    #         students_objects = self.env['student.student'].search([('parent_id','=',self.id)])
    #         fees_payment = self.env['fees.payment']
    #         student_list = []
    #         payment_list = []
    #         total_list = []
    #         for student in students_objects:
    #             print(student)
    #             student_object = {'id':student.id,'name':student.name,'student_sequence':student.student_sequence}
    #             print(student_object )
    #             total_list.append(student_object )
    #             # total_list.append(student_list)
    #             this_payments = fees_payment.search([('student_id','=',student.id)])
    #             if this_payments:
    #                 for payment in this_payments:
    #                     payment_obj = {'ID':payment.id,'Code':payment.name,'Next':payment.invoice_installment,}
    #                     total_list.append(payment_obj)
    #         print(total_list)
    #         return total_list

    def get_parents(self):
        """ Definition that gets the parent information including the children and there payments """
        parents_list = self.env['res.partner'].search_read([('is_parent', '=', True)])
        parents = []
        for parent in parents_list:
            children = self.get_parent_child(parent['id'])
            parent_obj = {
                'code': parent['id'],
                'name': parent['name'],
                'children': children
            }
            parents.append(parent_obj)
        print(parents)
        return parents

    def get_parent_child(self, parent_id):
        """ Definition that gets the children information and there payments takes parent_id """
        print('get_parent_child called')
        child_list = self.env['student.student'].search_read([('parent_id', '=', parent_id)])
        children = []
        for child in child_list:
            invoices = self.get_student_invoices(child['invoice_ids'])
            child_obj = {
                'code': child['id'],
                'name': child['name'],
                'payments': invoices
            }
            children.append(child_obj)
        return children

    def get_student_invoices(self, ids):
        """ Definition that gets the payments information takes a set of child_ids """
        print('get_student_invoices called')
        invoices_list = self.env['account.invoice'].search_read([('id', 'in', ids)])
        invoices = []
        for invoice in invoices_list:
            invoice_obj = {
                'state': invoice['state'],
                'source_document': invoice['origin'],
                'amount_untaxed': invoice['amount_untaxed'],
                'tax': invoice['amount_tax'],
                'amount_total': invoice['amount_total'],
            }
            invoices.append(invoice_obj)
        return invoices
