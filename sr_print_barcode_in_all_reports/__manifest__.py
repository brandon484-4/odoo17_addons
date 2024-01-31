# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) Sitaram Solutions (<https://sitaramsolutions.in/>).
#
#    For Module Support : info@sitaramsolutions.in  or Skype : contact.hiren1188
#
##############################################################################

{
    'name': "Print barcode in sales order, invoice, inventory, and purchase order reports",
    'version': "17.0.0.0",
    'summary': "Print barcode in sales orders, invoices, inventory, and purchase reports",
    'category': 'Extra Tools',
    'description': """
    print barcode in all odoo reports
    barcode in reports
    odoo reports with barcode
    ean13 barcode in odoo reports
    code 128 barcode in odoo reports
    odoo qweb reports with barcode
    barcode in odoo qweb reports
    sales order reports with barcode barcode in sales order pdf report print barcode in sales order qweb report
    purchase order report with barcode barcode in purchase order pdf report print barcode in purchase order qweb report
    request for quotation report with barcode barcode in request for quotation pdf report print in request for quotation qweb report
    customer invoice reports with barcode barcode in customer invoice pdf report print in customer invoice qweb report
    vendor bills reports with barcode barcode in vendor bill pdf report print barcode in vendor bill qweb report
    inventory report with barcode barcode in inventory report pdf report print barode in inventory qweb report
    inherit sales order report template
    inherit customer invoice report template
    inherit vendor bill report template
    inherit inventory report template
    inherit purchase order report template
    inherit request for quotation template
    
    """,
    'author': "Sitaram",
    'website':"http://www.sitaramsolutions.in",
    'depends': ['base', 'sale_management', 'purchase', 'stock', 'account','web'],
    'data': [
        'reports/inherited_sale_order_report.xml',
        'reports/inherited_invoice_order_report.xml',
        'reports/inherited_purchase_order_report.xml',
        'reports/inherited_delivery_order_report.xml'
    ],
    'demo': [],
    "external_dependencies": {},
    "license": "OPL-1",
    'installable': True,
    'auto_install': False,
    'live_test_url':'https://youtu.be/50QLwLVItSs',
    'images': ['static/description/banner.png'],
    
}
