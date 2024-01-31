# See LICENSE file for full copyright and licensing details.
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = "res.company"

    custom_report_background_image = fields.Binary(string="Custom Report Background")
    # New field. #22260
    is_bg_per_lang = fields.Boolean(
        string="Is Background Per Language",
    )
    bg_per_lang_ids = fields.One2many(
        "report.background.lang",
        "company_id",
        string="Background Per Language",
    )

    @api.constrains("is_bg_per_lang", "bg_per_lang_ids")
    def _check_company_custom_bg_config(self):
        """New constrains method for check custom bg per company is set or not when
        'From Company' type is set at ir_actions_report level. #22260"""
        # Env.
        report_env = self.env["ir.actions.report"]
        # Search report based on the 'company' type and 'is_bg_per_lang' boolean.
        report_ids = report_env.search(
            [
                ("custom_report_type", "in", ["company", False]),
                ("is_bg_per_lang", "=", True),
            ]
        )
        # Search dynamic reoprt.
        dynamic_report_ids = report_env.search(
            [
                ("custom_report_type", "=", "dynamic"),
                ("is_bg_per_lang", "=", True),
            ]
        )
        is_fall_back_to_company = False
        if dynamic_report_ids:
            # Get report in which Fall back to company is true.
            is_fall_back_to_company = dynamic_report_ids.mapped(
                "background_ids"
            ).filtered(lambda r: r.fall_back_to_company)
        # If fall_back_to_company and custom bg per lang is not set then raise warning.
        if is_fall_back_to_company and not (
            self.is_bg_per_lang and self.bg_per_lang_ids
        ):
            raise UserError(
                _(
                    "Please configure Custom Background Per Language because "
                    "'Fall Back To Company' is set in the dynamic type report level!"
                )
            )
        # If any report with company type and custom bg per lang is not set at
        # res_company level then raise warning.
        if report_ids and not (self.is_bg_per_lang and self.bg_per_lang_ids):
            raise UserError(
                _(
                    "Please configure Custom Background Per Language because "
                    "'From Company' type is set at the Report level!"
                )
            )
