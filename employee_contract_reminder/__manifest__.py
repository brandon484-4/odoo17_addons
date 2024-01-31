# -*- coding: utf-8 -*-
{
    'name': "Employee Contract Reminder",

    'summary': """
        This module will send an email to the employee when the contract is about to expire.
    """,

    'description': """
        This module will send an email to the employee when the contract is about to expire.
    """,

    'author': "Agung Sepruloh",
    'website': "https://github.com/agungsepruloh",
    'maintainers': ['agungsepruloh'],
    'license': 'LGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Generic Modules/Human Resources',
    'version': '17.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_contract'],

    # always loaded
    'data': [
        # Views
        'views/res_config_settings_views.xml',

        # Data
        'data/ir_cron_data.xml',
        'data/mail_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],

    'images': ['static/description/banner.gif'],
    'application': True,
}
