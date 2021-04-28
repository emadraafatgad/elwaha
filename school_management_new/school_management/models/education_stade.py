from odoo import fields, models, api


class EducationalStage(models.Model):
    _name = 'education.stage'

    name = fields.Char(required=True)
    code = fields.Char(readonly=True)
    classera_id = fields.Integer('Classera ID',readonly=True,stored=True,copied=True)

    _sql_constraints = [
        ('classera_id_uniq', 'UNIQUE (classera_id)', 'You can not have two records with the same Classera ID !'),
        ('code_uniq', 'UNIQUE (code)', 'Sequence Must Be Unique')
    ]

    @api.model
    def create(self, vals):
        '''Method to create user when student is created'''
        vals['code'] = self.env['ir.sequence'].next_by_code('student.student') or '/'
        res = super(EducationalStage, self).create(vals)

        return res


class EducationStageYear(models.Model):
    _name = 'education.stage.year'

    name = fields.Char(required=True)
    code = fields.Integer(string="Sequence",readonly=False)
    stage_id = fields.Many2one('education.stage',required=True)
    classera_id = fields.Integer('Classera ID', readonly=True, stored=True, copied=True)

    _sql_constraints = [
        ('classera_id_uniq', 'UNIQUE (classera_id)', 'You can not have two records with the same Classera ID !'),
        ('code_uniq', 'UNIQUE (code)', 'Sequence Must Be Unique')
    ]

    @api.model
    def create(self, vals):
        vals['code'] = self.env['ir.sequence'].next_by_code('education.stage.year')
        return super(EducationStageYear, self).create(vals)


class EducationClasses(models.Model):
    _name = 'education.classes'

    name = fields.Char()
    stage_year = fields.Many2one('education.stage.year')
    capacity = fields.Integer(required=True)
    classera_id = fields.Integer('Classera ID', readonly=True, stored=True, copied=True)

    _sql_constraints = [
        ('classera_id_uniq', 'UNIQUE (classera_id)', 'You can not have two records with the same Classera ID !'),

    ]

