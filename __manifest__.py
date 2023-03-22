# -*- coding: utf-8 -*-
{
    'name': "Advance / Imprest",

    'summary': """
        Do Imprest Applications and Retirements""",

    'description': """
        Do Imprest Applications and Retirements
    """,

    'author': "SuperCom Tanzania Limited",
    'website': "http://www.supercom.co.tz",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    # 'depends': ['base','mail','hr','om_account_accountant'],
    'depends': ['base','mail','hr','account','report_xlsx','project','mst_imprest','account'],

    # always loaded

    'data': [
        # 'security/security.xml',
        'security/imprest_security.xml',
        'security/ir.model.access.csv',
        'views/email_template.xml',
        'wizard/reason_wizard_view.xml',
        'wizard/reason_wizard_view_retire.xml',
        'views/certify_limit_view.xml',
        'views/imprest_application.xml',
        'views/imprest_retirement.xml',
        'reports/imprest_application_report.xml',
        'reports/imprest_retirement_report.xml',
        'reports/fleet_application_report.xml',
        'reports/plane_report.xml',
        'views/sequence.xml',
        'views/mst_test.xml',
    ],

    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
