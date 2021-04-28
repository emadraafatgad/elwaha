
{
    'name': 'Classera School Management',
    'version': '12.0.1.0.0',
    'author': 'Classera E-Learning ',
    'website': 'http://www.classeera.com',
    'category': 'School Management',
    'license': "AGPL-3",
    'complexity': 'easy',
    'Summary': 'A Module For School Management',
    'images': ['static/description/EMS.jpg'],
    'depends': ['account','classera_add_ar_eg_sr_lang', 'hr', 'crm', 'sale','hr_payroll'],
    'data': [
        'security/school_security.xml',
        'security/ir.model.access.csv',

        'views/menu_items.xml',
        'views/fees_rule.xml',
        'views/fees_rule_line.xml',
        'views/academic_year.xml',
        'views/nationality.xml',
        'views/fees_type.xml',
        'views/education_stage.xml',
        'views/student_view.xml',
        'views/fees_rule_structure.xml',
        'views/fees_payment_structure.xml',
        'views/partner_form.xml',
        'hr_views/hr_employee.xml',
        'wizard/payment_batches_generate.xml',
        'views/payment_batches.xml',


    ],
    'demo': ['demo/school_demo.xml'],
    'installable': True,
    'application': True,
    'sequence':1
}