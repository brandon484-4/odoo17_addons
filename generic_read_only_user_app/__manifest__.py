# -*- coding: utf-8 -*-

{
    'name': 'Generic Read Only User Access',
    "author": "Edge Technologies",
    'version': '1.0',
    'summary': "Read only access to user limited access rights to user user limited access read only user access user read only access user restricted access restriction on user access read only user read only access login user read only access limited portal user access",
    'description': """ This app provides a functionality to make generic user access read only for a particular login user set user read only
    Restriction on user level. stop user access from the system. user restriction user read only restriction. restricated user access. limited user access limited. security restriction on user level. user security restriction.

Limited access rights to user
User limited access
Read only user access
User read only access
User restricted access
Restriction on user access
Read only user
User read only access
Login user read only access
Login user limited access
Login user restricted access
User access restriction 
Login user access restriction
User security access restriction
User security restriction
Customer read only access
Supplier read only access
Vendor read only access
Limited customer access

    """,
    "license" : "OPL-1",
    'live_test_url': "https://youtu.be/J2k28TUCbZo",
    "images":['static/description/main_screenshot.png'],
    'depends': ['base','sale_management'],
    'data': [
            'security/user_read_only_group.xml',
            'security/ir.model.access.csv',
            'views/res_user_read_only.xml',
            ],
    'installable': True,
    'auto_install': False,
    'category': 'Extra Tools',
}
