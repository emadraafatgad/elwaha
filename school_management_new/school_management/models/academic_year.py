from odoo import fields, models, api, _
from odoo.exceptions import Warning
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class Product(models.Model):
    _inherit = 'product.product'

    is_fees = fields.Boolean()


class AcademicSemester(models.Model):
    _name = 'academic.year.semester'

    name = fields.Char(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    academic_year = fields.Many2one('academic.year')
    classera_id = fields.Integer('Classera ID', readonly=True, stored=True, copied=True)

    _sql_constraints = [
        ('classera_id_uniq', 'UNIQUE (classera_id)', 'You can not have two semester with the same Classera ID !')
    ]

    @api.constrains('start_date', 'end_date')
    def dates_constrains(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                if rec.start_date > rec.end_date:
                    raise Warning(_("You Can't Choose Start Date After End Date"))

    @api.onchange('start_date', 'end_date')
    def onchange_date(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise Warning(_('End date should be greater than start date.'))


class AcademicYear(models.Model):
    ''' Defines an academic year '''
    _name = "academic.year"
    _description = "Academic Year"

    name = fields.Char('Name', required=True, help='Name of academic year')
    # code = fields.Char('Code', readonly=True, help='Code of academic year')
    current = fields.Boolean('Current', help="Set Active Current Year")
    description = fields.Text('Description')
    semester_ids = fields.One2many('academic.year.semester', 'academic_year')
    classera_id = fields.Integer('Classera ID', readonly=True, stored=True, copied=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    semester_numbers = fields.Integer()

    @api.constrains('semester_numbers')
    def check_semester_int(self):
        if self.semester_numbers <= 0:
            raise ValidationError(_("Semester Numbers Must Be Bigger than 0"))

    _sql_constraints = [
        ('classera_id_uniq', 'UNIQUE (classera_id)', 'You can not have two Academic with the same Classera ID !'),
    ]

    @api.constrains('start_date', 'end_date')
    def prevent_date(self):
        if self.start_date > self.end_date:
            raise ValidationError(_("End date should be greater than start date."))
        next_years = fields.Date.today() + relativedelta(years=2)
        print(next_years)
        if self.start_date > next_years:
            raise ValidationError(_("start date must be in logic"))
        if self.end_date > next_years:
            raise ValidationError(_("end date must be in logic"))

    @api.constrains('current')
    def remove_chek_date(self):
        academic_years = self.env['academic.year'].search([])
        count = False
        for lin in academic_years:
            if lin.current == True and not count:
                count = True
            elif lin.current == True and count:
                raise ValidationError(_("There is must be only one current Academic year"))

    def update_academic_year(self, classera_id, values):
        """ Definition that gets the children information and there payments takes parent_id """
        print('get_parent_child called')
        acadmic_year = self.env['academic.year'].search([('classera_id', 'in', classera_id)], limit=1)[0]
        try:
            acadmic_respone = acadmic_year.write(values)
            return acadmic_respone
        except:
            return {'message': "NOt Found Academic Year"}

    def generate_academic_semester(self):
        if self.start_date >= self.end_date:
            raise UserError(_('End date should be greater than start date.'))
        else:
            self.semester_ids = [(5, 0, 0)]
            diff_days = (self.end_date - self.start_date).days
            print(diff_days, "Date Diff")
            semester_days = diff_days / self.semester_numbers
            print(semester_days, "semester_days")
            counter = 1
            start_date = self.start_date
            end_date = self.end_date
            next_date = start_date
            semester_obj = self.env['academic.year.semester']
            for semesters in range(0, self.semester_numbers):
                name = "semster " + str(counter)
                print(name)
                sem_start_date = next_date
                sem_end_date = next_date + timedelta(days=semester_days)
                print(sem_end_date)
                val = {
                    'name': name,
                    'start_date': sem_start_date,
                    'end_date': sem_end_date,
                    'academic_year': self.id,
                    # 'classera_id':counter
                }
                print(val, self.start_date, sem_start_date)
                sem_id = semester_obj.create(val)
                print(sem_id)
                counter = counter + 1
                next_date = sem_end_date + timedelta(days=1)
            semesters = self.env['academic.year.semester'].search_read([('academic_year', '=', self.id)])
            return {
                'message': 'Semesters created successfully.',
                'semesters': semesters
            }
