# See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ReportCompanyBackgroundLang(models.Model):
    _name = "report.company.background.lang"
    _description = "Report Company Background Line Per Language"

    # New fields. #T5886
    lang_id = fields.Many2one("res.lang", string="Language", ondelete="cascade")
    background_pdf = fields.Binary(string="Background PDF", required=True)
    file_name = fields.Char()
    report_id = fields.Many2one(
        "ir.actions.report", string="Report", ondelete="cascade"
    )
    company_id = fields.Many2one("res.company", string="Company", ondelete="cascade")
    type_attachment = fields.Selection(
        [
            ("background", "Background"),
            ("append", "Append"),
            ("prepend", "Prepend"),
        ],
        string="Type",
        default="background",
        required=True,
    )
