# See LICENSE file for full copyright and licensing details.
{
    "name": "Custom Background",
    "version": "17.0.1.0.0",
    "author": "BizzAppDev Systems Pvt. Ltd.",
    "website": "http://www.bizzappdev.com",
    "category": "GenericModules",
    "depends": ["base", "web"],
    "summary": "Custom  Background",
    "images": ["images/image.png"],
    "init_xml": [],
    "data": [
        "security/ir.model.access.csv",
        "views/ir_actions.xml",
        "views/res_company_view.xml",
    ],
    "installable": True,
    "application": False,
    "assets": {
        "web.report_assets_common": [
            "/custom_background/static/src/scss/report_qweb_pdf.scss",
        ],
    },
    "license": "Other proprietary",
}
