# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
{
    'name': "Employee Accommodation Management",
    'version': '17.0.0.0',
    'category': 'Human Resources',
    'summary': "Create Accommodation Request form Employee Expense Accommodation Employee Accommodation Booking Employee Housing Arrangements HR Manager Approval on Employee Accommodation PDF Report Generate Expense of Employee Accommodation Policy Employee Room Allocation",
    'description': """
        
        Employee Accommodation Odoo App helps users to creating accommodation request from the employee. User can give an access rights as HR and Manager for employee accommodation also they can create multiple hotels in the location. User can create accommodation for employee and submit to the manager for approvals. HR/Manager have access to approve or reject the request and generate an expense of employee accommodation. User can print the employee accommodation report in PDF format.
    
    """,
    "author": "BrowseInfo",
    "website" : "https://www.browseinfo.com",
    'depends': ['base','hr','mail','hr_expense'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence_data.xml',
        'report/employee_accommodation_print_report.xml',
        'report/empoyee_accommodation_pdf.xml',
        'views/bi_hotel_views.xml',
        'views/bi_location_views.xml',
        'views/employee_accommodation_views.xml',
        'wizard/reject_reason_wizard_views.xml',
    ],
    'license':'OPL-1',
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/ZHbdwHT_fKU',
    "images":['static/description/Employee-Accommodation-Banner.gif'],
}
