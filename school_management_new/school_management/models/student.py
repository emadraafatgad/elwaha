import time
import base64
from datetime import date
from odoo import models, fields, api, tools, _
from odoo.modules import get_module_resource
from odoo.exceptions import except_orm
from odoo.exceptions import ValidationError

# from lxml import etree
# added import statement in try-except because when server runs on
# windows operating system issue arise because this library is not in Windows.
try:
    from odoo.tools import image_colorize, image_resize_image_big
except:
    image_colorize = False
    image_resize_image_big = False


class MotherTongue(models.Model):
    _name = 'mother.toungue'
    _description = "Mother Toungue"

    name = fields.Char("Mother Tongue")


class StudentSequence(models.Model):
    _name = 'student.sequence'

    name = fields.Char(required=True)
    sequence = fields.Integer(required=True)


class StudentStudent(models.Model):
    ''' Defining a student information '''
    _name = 'student.student'
    _description = 'Student Information'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _inherits = {
        'res.partner': 'partner_id',
    }

    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='cascade',
                                 help='Partner-related data of the student')

    classera_id = fields.Integer('Classera ID', readonly=True, stored=True, copied=True)

    _sql_constraints = [
        ('classera_id_uniq', 'UNIQUE (classera_id)', 'You can not have two records with the same Classera ID !')
    ]

    @api.depends('date_of_birth')
    def _compute_student_age(self):
        '''Method to calculate student age'''
        current_dt = date.today()
        for rec in self:
            if rec.date_of_birth:
                start = rec.date_of_birth
                age_calc = ((current_dt - start).days / 365)
                # Age should be greater than 0
                if age_calc > 0.0:
                    rec.age = age_calc

    @api.constrains('date_of_birth')
    def check_age(self):
        '''Method to check age should be greater than 5'''
        current_dt = date.today()
        if self.date_of_birth:
            start = self.date_of_birth
            age_calc = ((current_dt - start).days / 365)
            # Check if age less than 5 years
            if age_calc < 5:
                raise ValidationError(_('''Age of student should be greater than 5 years!'''))

    @api.model
    def create(self, vals):
        '''Method to create user when student is created'''
        vals['is_student'] = True
        vals['customer'] = True
        vals['type'] = 'contact'
        vals['code'] = self.env['ir.sequence'].next_by_code('student.student') or '/'
        res = super(StudentStudent, self).create(vals)
        res.add_parent_id()
        return res

    def add_parent_id(self):
        partner_id = self.env['res.partner'].search([('id', '=', self.partner_id.id)])
        print(partner_id.name, self.name, self.parent_id.name)
        partner_id.parent_id = self.parent_id
        print(partner_id.parent_id.name)

    @api.model
    def check_current_year(self):
        '''Method to get default value of logged in Student'''
        res = self.env['academic.year'].search([('current', '=',
                                                 True)])
        if not res:
            raise ValidationError(_('''There is no current Academic Year
                                    defined!Please contact to Administator!'''
                                    ))
        return res.id

    # parent_id = fields.Many2one('res.partner',domain="[('is_parent','=',True),('company_type','=','company')]")
    parent_id = fields.Many2one('res.partner', string='Parent', index=True)
    code = fields.Char('Student Code', readonly=True)
    year = fields.Many2one('academic.year', 'Academic Year', readonly=True,
                           default=check_current_year)
    # relation = fields.Many2one('student.relation.master', 'Relation')

    admission_date = fields.Date('Admission Date')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')],
                              'Gender')
    date_of_birth = fields.Date('BirthDate', required=True,
                                )
    mother_tongue = fields.Many2one('mother.toungue', "Mother Tongue")
    age = fields.Integer(compute='_compute_student_age', string='Age',
                         readonly=True)
    maritual_status = fields.Selection([('unmarried', 'Unmarried'),
                                        ('married', 'Married')],
                                       'Marital Status',
                                       )
    blood_group = fields.Char('Blood Group')

    nationality_id = fields.Many2one('school.nationality')
    Acadamic_year = fields.Char('Year', related='year.name',
                                help='Academic Year', required=True)
    education_stage = fields.Many2one('education.stage', string="Stage")
    stage_level = fields.Many2one('education.stage.year', string="Stage Leave",
                                  domain="[('stage_id','=',education_stage)]")
    education_class_id = fields.Many2one('education.classes',string="Class",domain="[('stage_year','=',stage_level)]")
    student_sequence = fields.Selection([(1, 'The First'), (2, 'The Second'),
                                         (3, 'The Third'), (4, 'The Fourth'), (5, 'The Fifth')],
                                        compute='student_arrangement_parent', store=True,  string="Student Sequence")

    student_sequence_id = fields.Many2one('student.sequence',compute='student_arrangement_parent',
                                          string="Student Sequence" , store=True)
    student_sequence_id_ids = fields.Many2one('student.sequence')
    active = fields.Boolean(default=True)
    fees_type = fields.Many2many('fees.type',string="Fees Amount",domain="[('education_stage_year','=',stage_level),('academic_year','=',year)]")

    @api.depends('parent_id')
    def student_arrangement_parent(self):
        for rec in self:
            if rec.parent_id:
                student_obj = self.env['student.student']
                students_count = student_obj.search([('parent_id','=',rec.parent_id.id)])
                count = 0
                for student in students_count:
                    if not student.id == rec.id:
                        print(student.name,rec.name)
                        print(student.id, rec.id)
                        count = count+1
                        print(count,"   =   students_count")
                this_sequence = self.env['student.sequence'].search([('sequence','=',count+1)])
                print(this_sequence,"this sequence")
                if this_sequence:
                    rec.student_sequence_id = this_sequence
                else:
                    raise ValidationError(_("It is not found "))
                # if count  < 5:
                #     rec.student_sequence = count+1
                # if count == 6:
                #     print("666666666666666")

    def create_student(self, paren_classera_id, values):
        """ Definition that gets the children information and there payments takes parent_id """
        print('get_parent_child called')
        parent_obj = self.env['res.partner'].search([('classera_id', 'in', paren_classera_id)], limit=1)[0]
        parent_id = parent_obj.id
        student_obj = self.env['student.student']
        val = {'name': values['name'],
               'gender': values['gender'],
               'date_of_birth': values['date_of_birth'],
               'stage_level': values['stage_level'],
               'nationality_id': values['nationality_id'],
               'parent_id': parent_id,
               'classera_id': values['classera_id'],
               }
        try:
            student_respone = student_obj.create(val)
            return student_respone
        except:
            return {'message': "Cant craete"}


class ResPartner(models.Model):
    _inherit = 'res.partner'
    student_ids = fields.One2many('student.student', 'parent_id')


class EducationClass(models.Model):
    _inherit = 'education.classes'

    student_ids = fields.One2many('student.student','education_class_id')