# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>)

{
    'name': 'Birthday Notification',
    'version': '1.0',
    'category': 'Tools',
    'depends': ['base_setup', 'hr', 'contacts'],
    'license': 'OPL-1',
    'author': 'Kanak Infosystems LLP.',
    'website': 'https://kanakinfosystems.com',
    'summary': 'Birthday Wishes to Employees & Contacts',
    'description': """
        This module send email notification for birthday wish to employees and contacts. | Birthday blessings. |Birthday card. | Birthday cheer. | Birthday notification. | Birthday greeting. | Birthday message. | Birthday reminder. | Birthday wishes. | Bliss. | Email notification. | Joyous occasion. | Moment. |Special day. | Wishes. | Your day.
    """,
    'images': ['static/description/banner.jpg'],
    'data': [
        'data/knk_mail_data.xml',
        'data/knk_cron_data.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True
}
