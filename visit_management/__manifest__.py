# -*- coding: utf-8 -*-
{
	'name': 'Cureleads Visits Management',
	'version': '12.0.15.0.0',
	'summary': 'Full Feature For Visits Management',
	'category': 'Gym',
	'author': 'Emad Raafat',
	'maintainer': 'Emad Techno Solutions',
	'company': 'Emad group Solutions',
	'website': 'https://www.emad-odoo.com',
	'depends': ['base','sale','hr',],
	'data': [
		'security/security.xml',
		'security/ir.model.access.csv',
		'views/class_visits.xml',
		'views/visits_plans.xml',
		'views/employee_visits.xml',
		'views/client_visits.xml',
		'views/visits_reports.xml',
		'report/visit_management_report.xml',
		# 'views/class_plan.xml',
		# 'views/class_plan_line.xml',
		'views/visit_plan_report.xml'
	],
	'images': [],
	'license': 'AGPL-3',
	'installable': True,
	'application': True,
	'auto_install': False,
	'sequence':1
}
