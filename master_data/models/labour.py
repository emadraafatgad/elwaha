# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, SUPERUSER_ID, fields, models, _
from datetime import date
from odoo.exceptions import UserError,ValidationError


class LaborSkills(models.Model):
    _name = 'labor.skills'

    name = fields.Char(required=True)
    for_men = fields.Boolean()

class LaborSpecification(models.Model):
    _name = 'labor.specifications'
    name = fields.Char(required=True)

class LaborProfile(models.Model):
    _name = 'labor.profile'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _inherits = {
        'res.partner': 'partner_id',
    }
    _description = 'Labor Profile'

    SEX = [
        ('Male', 'Male'),
        ('Female', 'Female'),
    ]

    state = fields.Selection([('new', 'New'), ('editing', 'Editing'), ('confirmed', 'Confirmed')],default="new",track_visibility="onchange")
    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='cascade',
                                 help='Partner-related data of the patient')
    age = fields.Integer(compute='_compute_slave_age',store=True)
    gender = fields.Selection(SEX, string='Gender', index=True,required=True)
    # country_id = fields.Many2one('res.country', string='Nationality')
    identification_code = fields.Char(string='Labor Code', copy=True,index=True,default=lambda self: _('New'),
                                      help='Labor Identifier provided by the Health Center', readonly=True)
    national_id = fields.Char(size=14, string='National ID')
    card_no = fields.Char()
    start_date = fields.Date('Issued Date')
    end_date = fields.Date('Expiry/Expiration Date')

    general_info = fields.Text(string='General Information', help="General information about the patient")
    have_skills = fields.Boolean()
    skills_ids = fields.Many2one('labor.skills')
    occupation = fields.Selection([('house_maid', 'House Maid'), ('pro_maid', 'Pro Maid'),('pro_worker','Pro Worker')],
                                  default="house_maid", string='Occupation',required=True)
    salary = fields.Float()
    agent = fields.Many2one('res.partner',domain=[('vendor_type', '=','agent')],required=True)
    experience_ids = fields.One2many('prior.experience','laborer_id')
    language = fields.Many2many('res.lang',required=True)
    specifications = fields.Many2many('labor.specifications')
    height = fields.Float()
    weight = fields.Float()
    general_remarks = fields.Text()
    children = fields.Char()
    other_mob = fields.Char('Other Mob')
    marital_status = fields.Selection([('single', 'Single'), ('married', 'Married'), ('windowed', 'Windowed'), ('divorced', 'Divorced')],'Marital Status',required=True)
    religion = fields.Selection([('muslim', 'Muslim'), ('christian', 'Christian'), ('jew', 'Jew'), ('other', 'Other')],'Religion',required=True)
    children_ids = fields.One2many('children.number', 'laborer_id')
    education_certificate = fields.Selection([('primary', 'Primary Education'), ('preparatory', 'Preparatory Education'), ('secondary', 'Secondary Education'), ('university', 'University'),('diploma', 'Diploma'), ('no_education', 'No Education')],'Educational Certificate',required=True)
    end_education = fields.Char('Education Remarks')
    no_education = fields.Char('Remarks')
    prn = fields.Char('PRN NO')
    register_with = fields.Selection([('national_id', 'National ID'), ('nira', 'Nira'), ('passport', 'Passport')],'Document',required=True)
    allow_passport_request = fields.Boolean('Allow Passport Request')

    lc1 = fields.Many2one('labor.village', string='Village /LC1', required=True)
    lc2 = fields.Many2one('labor.parish', string='Parish /LC2', required=True)
    lc3 = fields.Many2one('labor.subcounty', string='Sub County /LC3', required=True)
    lc4 = fields.Many2one('labor.county', string='County /LC4', required=True)
    district = fields.Many2one('labor.district', string='District', required=True)
    origin_lc1 = fields.Many2one('labor.village', string='Village /LC1', required=True)
    origin_lc2 = fields.Many2one('labor.parish', string='Parish /LC2', required=True)
    origin_lc3 = fields.Many2one('labor.subcounty', string='Sub County /LC3', required=True)
    origin_lc4 = fields.Many2one('labor.county', string='County /LC4', required=True)
    origin_district = fields.Many2one('labor.district', string='District', required=True)
    origin_tribe = fields.Many2one('labor.tribe', string='Tribe', required=True)
    origin_clan = fields.Many2one('labor.clan', string='Clan', required=True)
    origin_descendants = fields.Char(string='Descendants')
    interpol_no = fields.Char('Interpol No')
    interpol_start_date = fields.Date('Interpol Start Date')
    interpol_end_date = fields.Date('Interpol End Date')
    allow_passport = fields.Boolean('Bear the expenses/Passport',readonly=True)
    large_image = fields.Binary()
    after_medical_check = fields.Selection([('fit', 'Fit'),('unfit', 'Unfit'),('pending', 'Pending')])
    medical_unfit_reason = fields.Char()
    agency = fields.Many2one('res.partner',domain=[('agency','=',True)])
    agency_code = fields.Many2one('specify.agent')
    specify_agency = fields.Selection([('draft', 'draft'),('available', 'Available'), ('selected', 'Selected'), ('done', 'done')], default='draft', track_visibility="onchange")

    @api.onchange('date_of_birth')
    def _check_age(self):
        if self.date_of_birth:
            if self.age < 21 or self.age > 38:
                return {
                    'warning': {'title': _('Age Warning'),
                                'message': _('Age equals %s years.') % self.age }
                }


    def _default_user(self):
        user = self.env.uid
        return user


    interview_by = fields.Many2one('res.users',default=_default_user,required=True,track_visibility='onchange')

    @api.multi
    def action_confirm(self):
        if self.occupation == 'house_maid':
            self.identification_code = self.env['ir.sequence'].next_by_code('house.maid')
            training_req = self.env['slave.training']
            training_req.create({
                'slave_id': self.id,
            })
        elif self.occupation == 'pro_worker':
            self.identification_code = self.env['ir.sequence'].next_by_code('pro.worker')
        elif self.occupation == 'pro_maid':
            self.identification_code = self.env['ir.sequence'].next_by_code('pro.maid')
        else:
            self.identification_code = 'No Occupation'
        if self.register_with == 'national_id':
            request_obj = self.env['passport.request']
            request_obj.create({
                'labor_id': self.id,
                'national_id': self.national_id,
            })
        if self.register_with == 'nira':
            self.request_nira()
        if self.passport_no:
            self.request_interpol()
            self.big_medical_request()
            self.specify_agency_request()
        self.state = 'confirmed'

    @api.multi
    def action_unlock(self):
        self.state = 'editing'

    @api.multi
    def action_lock(self):
        self.state = 'confirmed'



    @api.onchange('pass_start_date')
    def onchange_passport_date(self):
        if self.pass_start_date:
            self.pass_end_date = (self.pass_start_date + relativedelta(years=10)).strftime('%Y-%m-%d')
    @api.onchange('national_id')
    def onchange_national_id(self):
        if self.national_id:
            if len(self.national_id) < 14:
                message = _(('ID must be 14!'))
                mess = {
                    'title': _('Warning'),
                    'message': message
                }
                return {'warning': mess}

    @api.onchange('register_with')
    def _onchange_register(self):
        if self.register_with and not self.occupation:
            raise UserError(_('You must select occupation first'))
        if self.occupation in ('pro_worker','pro_maid') and self.register_with in ('national_id','nira'):
            self.allow_passport = True
            message = _((' %s ,Must register with passport')% \
                        self.occupation)
            mess = {
                'title': _('Warning'),
                'message': message
            }
            return {'warning': mess}





    @api.model
    def create(self, vals):
        vals['is_slave'] = True
        vals['customer'] = True
        return super(LaborProfile, self).create(vals)
    @api.onchange('register_with')
    def _onchange_register_with(self):
        if self.register_with == 'nira':
            self.national_id = ''

    def unlink(self):
        for record in self:
            if record.state == 'confirmed':
               raise ValidationError(_('Sorry, Confirmed Profile.'))
        return super(LaborProfile, self).unlink()



    @api.multi
    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id ,'%s-%s' %( rec.identification_code,rec.name)))
        return res
    experience_ids_len = fields.Integer()
    @api.constrains('experience_ids')
    def len_experience_ids(self):
        self.experience_ids_len = len(self.experience_ids)

    @api.constrains('age')
    def age_const(self):
        if self.age < 21 or self.age > 38:
            raise ValidationError(_('Sorry, Cannot accept %s years.') % self.age)



    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        if name:
            actions = self.search(['|', '|', '|', ('name', operator, name), ('phone', operator, name),
                                   ('identification_code', operator, name), ('national_id', operator, name)] + args,
                                  limit=limit)
            return actions.name_get()
        return super(LaborProfile, self)._name_search(name, args=args, operator=operator, limit=limit)



    registration_date = fields.Datetime('Registration Time', readonly=True, index=True, default=fields.Datetime.now)
    date_of_birth = fields.Date("Date of Birth",required=True)
    pre_medical_check = fields.Selection([('Fit', 'Fit'),
                                          ('Unfit', 'Unfit')], default='Fit',required=True)
    reason = fields.Char()
    relative_ids = fields.One2many('partner.relatives', 'partner_id')
    vendor_type = fields.Selection([('Broker', 'Broker'), ('Tracker', 'Tracker'), ('Training', 'Training Center'),
                                    ('hospital', 'Hospital')])

    _sql_constraints = [
        ('phone_uniq', 'unique(phone)', 'Phone must be unique!'),('id_unique', 'unique(national_id)', 'National ID must be unique!')
        ,('passport_uniq', 'unique(passport_no)', 'Passport No must be unique!')
    ]

    @api.onchange('date_of_birth')
    def _compute_slave_age(self):

        """Updates age field when birth_date is changed"""

        if self.date_of_birth:
            d1 = datetime.strptime(self.date_of_birth, "%Y-%m-%d").date()

            d2 = date.today()

            self.age = relativedelta(d2, d1).years
    @api.depends('date_of_birth')
    def _compute_slave_age(self):
        '''Method to calculate student age'''
        current_dt = date.today()
        for rec in self:
            if rec.date_of_birth:
                start = rec.date_of_birth
                age_calc = ((current_dt - start).days / 365)
                # Age should be greater than 0
                if age_calc > 0.0:
                    rec.age = age_calc






    passport_available = fields.Boolean()
    passport_no = fields.Char()
    pass_start_date = fields.Date("Issued Date")
    pass_end_date = fields.Date("Expire Date")
    pass_from = fields.Char('Placing Issue')



    id_available = fields.Boolean("ID")

    def id_is_available(self):
        self.id_available = True


    hide_request_nira = fields.Boolean('Hide Nira Request')
    def request_nira(self):
        nira = self.env['nira.letter.request']
        nira.create({
            'labourer_id':self.id,
            'name': self.name,
            'code': self.identification_code,
            'birth_date': self.date_of_birth,


        })


    def move_passport_available(self):
        self.passport_available = True
        print("Available")

    hide_request_passport = fields.Boolean('Hide Passport Request')
    def passport_request(self):
        if self.state == 'confirmed':
            if self.national_id:
                request_obj = self.env['passport.request']
                request_obj.create({
                    'name': self.name,
                    'labor_id': self.id,
                    'national_id': self.national_id,
                })
            else:
                raise UserError(_('There is no ID,pleasr request ID first'))
        else:
            raise UserError(_('You must confirm Record First'))
        if self.passport_request:
            self.hide_request_passport = True

    hide_request_interpol = fields.Boolean('Hide Interpol Request')
    def request_interpol(self):

        if self.passport_no:
                interpol = self.env['interpol.request']
                interpol.create({
                    'labor_id': self.id,
                    'labor': self.name,
                    'national_id': self.national_id,
                    'passport_no': self.passport_no,

                })
        else:
            raise UserError(_('There is no Passport No'))

        if self.request_interpol:
            self.hide_request_interpol = True

    hide_request_medical = fields.Boolean('Hide Medical Request')
    def big_medical_request(self):
        if self.passport_no:
            interpol = self.env['big.medical']
            interpol.create({
                'labor_id': self.id,
                'labor': self.name,
                'national_id': self.national_id,
                'passport_no': self.passport_no,

            })
        else:
            raise UserError(_('There is no Passport No'))


        if self.big_medical_request:
            self.hide_request_medical = True

    def specify_agency_request(self):
        specify_agency = self.env['specify.agent']
        specify_agency.create({
            'labor_id': self.id,
            'labor_name': self.name,
            'passport_no': self.passport_no,
            'age': self.age,
            'religion': self.religion,
        })

    hide_request_training = fields.Boolean('Hide Training Request')
    def request_training(self):
        if self.state == 'confirmed':
            training_req = self.env['slave.training']
            training_req.create({
                'slave_id': self.id,
            })
        else:
            raise UserError(_('You must confirm record first'))
        if self.request_training:
            self.hide_request_training = True


class Expeience(models.Model):
    _name = 'prior.experience'

    laborer_id = fields.Many2one('labor.profile')
    country_id = fields.Many2one('res.country',string='Country')
    from_year = fields.Selection([(num, str(num)) for num in range(1900, (datetime.now().year)+1 )], 'From Year')
    to_year = fields.Selection([(num, str(num)) for num in range(1900, (datetime.now().year)+1 )], 'To Year')

class Children(models.Model):
    _name = 'children.number'

    laborer_id = fields.Many2one('labor.profile')
    number = fields.Char(string='#')
    age = fields.Integer(string='Age/Year')
    age_month = fields.Integer(string='Age/Month')




class LaborVillage(models.Model):
    _name = 'labor.village'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _sql_constraints = [('name_uniq', 'unique(Name)', 'Name must be unique!')]

    name = fields.Char(required=True)


class LaborParish(models.Model):
    _name = 'labor.parish'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _sql_constraints = [('name_uniq', 'unique(Name)', 'Name must be unique!')]
    name = fields.Char(required=True)


class LaborSubCounty(models.Model):
    _name = 'labor.subcounty'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _sql_constraints = [('name_uniq', 'unique(Name)', 'Name must be unique!')]
    name = fields.Char(required=True)

class LaborCounty(models.Model):
    _name = 'labor.county'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _sql_constraints = [('name_uniq', 'unique(Name)', 'Name must be unique!')]
    name = fields.Char(required=True)

class LaborDistrict(models.Model):
    _name = 'labor.district'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _sql_constraints = [('name_uniq', 'unique(Name)', 'Name must be unique!')]
    name = fields.Char(required=True)


class LaborTrip(models.Model):
    _name = 'labor.tribe'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _sql_constraints = [('name_uniq', 'unique(Name)', 'Name must be unique!')]
    name = fields.Char(required=True)


class LaborClan(models.Model):
    _name = 'labor.clan'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _sql_constraints = [('name_uniq', 'unique(Name)', 'Name must be unique!')]
    name = fields.Char(required=True)
