# -*- coding: utf-8 -*-
# Copyright 2004-2009 Tiny SPRL
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Clinic',
    'version': '12.0.1.0.0',
    'category': 'Medical',
    'depends': [
        'hr','base',
        'account',
        'product',
        'stock',
        'sale_management',
    ],
    'author': 'Emad Raafat',
    'website': 'https://odoo-community.org/',
    'license': 'AGPL-3',
    'data': [
        'security/medical_security.xml',
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/appointment.xml',
        'views/clinic_service_line.xml',
        'views/clinic_service.xml',
        'views/medical_patient.xml',
        'views/medical_doctor.xml',
        'views/appointment_config.xml',
        'views/appointment_stage.xml',
        'views/clinic_diagnosis.xml',
        'views/service_medicine.xml',
        'views/clinic_evaluation.xml',
        'views/clinic_prescription.xml',
        'views/clinic_service_package_line.xml',
        'views/clinic_service_package.xml',
        'views/medical_doctor_charge_config.xml',
        'views/medical_doctor_charge.xml',
        'views/appointment_session.xml',
        'report/appointment_report.xml',
        'report/evaluation_report.xml',
        'report/prescription_report.xml',
        # 'static/src/base.xml',
    ],
    'demo': [
        # 'demo/patient.xml',
    ],
    'installable': True,
	'application': True,
	'auto_install': False,
	'sequence':1,
}
