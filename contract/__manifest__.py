# -*- coding: utf-8 -*-
{
    'name': "ElWaha Contract",

    'summary': """
        New Contract For Elwaha 
        And shipment cycle
        """,

    'description': """
        this module to create new contract , 
        shipment plan and new clearance 
        
    """,

    'author': "Emad ",
    'website': "http://www.Emad.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'mrp',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','account','purchase','mrp'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/contract.xml',
        'views/port.xml',
        'views/packing.xml',
        'views/container_type.xml',
        'views/commodity_type.xml',
        'views/purchase_plan.xml',
        'views/purchase_project_plan.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
        "application": True,
        "installable": True,
}