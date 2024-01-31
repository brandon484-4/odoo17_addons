# See LICENSE file for full copyright and licensing details.
import base64
import logging
import os
import subprocess
import tempfile
from contextlib import closing
from itertools import islice

import lxml.html
from lxml import etree
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.graphics.barcode import createBarcodeDrawing

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import pdf, split_every
from odoo.tools.misc import find_in_path, ustr
from odoo.tools.safe_eval import safe_eval
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

try:
    createBarcodeDrawing(
        "Code128",
        value="foo",
        format="png",
        width=100,
        height=100,
        humanReadable=1,
    ).asString("png")
except Exception as e:
    _logger.info(e)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
_logger = logging.getLogger(__name__)


def _get_wkhtmltopdf_bin():
    return find_in_path("wkhtmltopdf")


def _split_table(tree, max_rows):
    """
    Walks through the etree and splits tables with more than max_rows rows into
    multiple tables with max_rows rows.

    This function is needed because wkhtmltopdf has a exponential processing
    time growth when processing tables with many rows. This function is a
    workaround for this problem.

    :param tree: The etree to process
    :param max_rows: The maximum number of rows per table
    """
    for table in list(tree.iter("table")):
        prev = table
        for rows in islice(split_every(max_rows, table), 1, None):
            sibling = etree.Element("table", attrib=table.attrib)
            sibling.extend(rows)
            prev.addnext(sibling)
            prev = sibling


class ReportBackgroundLine(models.Model):
    _name = "report.background.line"
    _description = "Report Background Line"

    page_number = fields.Integer()
    # TODO after 17 release need to change field name to ttype.
    type = fields.Selection(  # pylint: disable=W8113
        [
            ("fixed", "Fixed Page"),
            ("expression", "Expression"),
            ("first_page", "First Page"),
            ("last_page", "Last Page"),
            ("remaining", "Remaining pages"),
            ("append", "Append"),
            ("prepend", "Prepend"),
        ],
        string="Type",
    )
    background_pdf = fields.Binary(string="Background PDF")
    # New field. #22260
    file_name = fields.Char()
    report_id = fields.Many2one(
        comodel_name="ir.actions.report", string="Report", ondelete="cascade"
    )
    page_expression = fields.Char()
    fall_back_to_company = fields.Boolean()
    # New fields. #22260
    lang_id = fields.Many2one(
        comodel_name="res.lang", string="Language", ondelete="cascade"
    )


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    custom_report_background = fields.Boolean()
    custom_report_background_image = fields.Binary(string="Background Image")
    custom_report_type = fields.Selection(
        [
            ("company", "From Company"),
            ("report", "From Report Fixed"),
            ("dynamic", "From Report Dynamic"),
            # Added new custom report type #T5886
            (
                "dynamic_per_report_company_lang",
                "Background Per Report - Company - Lang",
            ),
        ]
    )

    background_ids = fields.One2many(
        "report.background.line", "report_id", "Background Configuration"
    )
    # New fields. #22260
    bg_per_lang_ids = fields.One2many(
        "report.background.lang",
        "report_id",
        string="Background Per Language",
    )
    is_bg_per_lang = fields.Boolean(
        string="Is Background Per Language",
    )
    # New field #T5886
    per_report_com_lang_bg_ids = fields.One2many(
        "report.company.background.lang",
        "report_id",
        string="Per Report Company Language Background",
    )

    def get_company_without_custom_bg(self):
        """New method for search and get company in which custom bg per language is not
        set. #22260"""
        res_company_env = self.env["res.company"].search([])
        # Filtered company in which is_bg_per_lang is not set and
        # attachment is not set.
        company = res_company_env.filtered(
            lambda c: not c.is_bg_per_lang or not c.bg_per_lang_ids
        )
        return company

    @api.constrains(
        "is_bg_per_lang",
        "bg_per_lang_ids",
        "custom_report_type",
        "background_ids",
        "custom_report_background",
    )
    def _check_report_custom_bg_config(self):
        """
        New constrains method for check custom bg per company is set or not when for
        'report' & 'dynamic' type. #22260
        """
        # If is_bg_per_lang is false then return.
        if not self.is_bg_per_lang or not self.custom_report_background:
            return
        # If type is 'report' and custom bg per lang is not set then raise warning.
        if self.custom_report_type == "report" and not self.bg_per_lang_ids:
            raise UserError(
                _("Please configure Custom Background Per Language for Report type!")
            )
        # If type is 'dynamic' and custom bg per lang is not set then raise warning.
        elif self.custom_report_type == "dynamic" and not self.background_ids:
            raise UserError(
                _("Please configure Custom Background Per Language for Dynamic type!")
            )
        # Check type is dynamic and background_ids is set or not.
        elif self.custom_report_type == "dynamic" and self.background_ids:
            # Filter fall_back_to_company true records.
            fbc = self.background_ids.filtered(lambda bg: bg.fall_back_to_company)
            # If fbc and custom bg not set at company level then raise warning.
            if fbc and self.get_company_without_custom_bg():
                raise UserError(
                    _(
                        "Please configure Custom Background Per Language in every "
                        "company!"
                    )
                )
        # If type is 'company' or type is not set then search
        # configuration in all company.
        elif (
            self.custom_report_type == "company" or not self.custom_report_type
        ) and self.get_company_without_custom_bg():
            # If any attachment not set in the any company then raise warning.
            raise UserError(
                _(
                    "Please configure Custom Background Per Language in every "
                    "company!"
                )
            )

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        """Inherit Method : Get the report. #24894"""
        if not self:
            report = self._get_report(report_ref)
        else:
            report = self
        # Get the model from the report. #24894
        Model = self.env[report.model]
        record_ids = Model.browse(res_ids)
        company_id = False
        if record_ids[:1]._name == "res.company":
            company_id = record_ids[:1]
        # Fix test cases error. #22107
        elif hasattr(record_ids[:1], "company_id"):
            # If in record company is not set then consider current log in
            # user's company. #22476
            company_id = record_ids[:1].company_id or self.env.user.company_id
        else:
            company_id = self.env.company

        # Add custom_bg_res_ids in context. #22260
        # Added the parameter "report_ref". #24894
        return super(
            IrActionsReport,
            self.with_context(custom_bg_res_ids=res_ids, background_company=company_id),
        )._render_qweb_pdf(report_ref=report_ref, res_ids=res_ids, data=data)

    def add_pdf_watermarks(self, custom_background_data, page):
        """
        New method : create a temp file and set datas and added in
        report page. #T4209
        """
        temp_back_id, temp_back_path = tempfile.mkstemp(
            suffix=".pdf", prefix="back_report.tmp."
        )
        back_data = base64.b64decode(custom_background_data)
        with closing(os.fdopen(temp_back_id, "wb")) as back_file:
            back_file.write(back_data)
        pdf_reader_watermark = PdfFileReader(temp_back_path, "rb")
        watermark_page = pdf_reader_watermark.getPage(0)
        watermark_page.mergePage(page)
        return watermark_page

    def get_lang(self):
        """
        New method for return language, if partner_id is available in model and
        partner is set in that model, else set current logged in user's language.
        #22260
        """
        res_record_ids = self._context.get("custom_bg_res_ids")
        model = self.env[self.model]
        record_ids = model.browse(res_record_ids)
        lang_code = False
        # If partner_id field in the model and partner is set in the model the consider
        # partner's language.
        # NOTE: Used "record_ids[:1]" to avoid loop, if use loop then always set last
        # record partner's language.
        if "partner_id" in model._fields and record_ids[:1].partner_id:
            partner_lang = record_ids[:1].partner_id.lang
            lang_code = partner_lang if partner_lang else "en_US"
        else:
            # If partner_id field is not in model or partner_id is not set then consider
            # current user's language.
            lang_code = self._context.get("lang")
        return lang_code

    def _get_background_per_report_company_language(self):
        """New method for get the custom background based on the report configuration
        based on the per company and per Lang. #T5886"""
        self.ensure_one()
        lang_code = self.get_lang()
        company = self._context.get("background_company")

        # Get the custom background if company and Lang are both matched. #T5886
        custom_background = self.per_report_com_lang_bg_ids.filtered(
            lambda bg: bg.type_attachment == "background"
            and bg.lang_id.code == lang_code
            and bg.company_id.id == company.id
        )
        if custom_background:
            return custom_background[:1].background_pdf

        # Get the custom background if company matched but Lang is not set. #T5886
        custom_bg_only_with_company = self.per_report_com_lang_bg_ids.filtered(
            lambda bg: bg.type_attachment == "background"
            and bg.company_id.id == company.id
            and not bg.lang_id.code
        )
        if custom_bg_only_with_company:
            return custom_bg_only_with_company[:1].background_pdf

        # Get the custom background if Lang matched but company is not set. #T5886
        custom_bg_only_with_lang = self.per_report_com_lang_bg_ids.filtered(
            lambda bg: bg.type_attachment == "background"
            and bg.lang_id.code == lang_code
            and not bg.company_id
        )
        if custom_bg_only_with_lang:
            return custom_bg_only_with_lang[:1].background_pdf

        # Get the custom background if Lang is not set and company is not set. #T5886
        default_custom_bg = self.per_report_com_lang_bg_ids.filtered(
            lambda bg: bg.type_attachment == "background"
            and not bg.lang_id
            and not bg.company_id
        )
        if default_custom_bg:
            return default_custom_bg[:1].background_pdf
        return False

    def get_bg_per_lang(self):
        """
        New method for get custom background based on the partner languages for
        report type and company type. #22260
        """
        company_background = self._context.get("background_company")
        lang_code = self.get_lang()
        # If custom_report_type is dynamic then set language related domains.
        if self.custom_report_type == "dynamic":
            # If is_bg_per_lang true then set lang_code related domain.
            if self.is_bg_per_lang:
                lang_domain = [
                    ("lang_id.code", "=", lang_code),
                ]
            else:
                # If is_bg_per_lang false then set lang_id related domain.
                lang_domain = [
                    ("lang_id", "=", False),
                ]
            return lang_domain
        # Call the method for get the custom background per company
        # and per Lang. #T5886
        if self.custom_report_type == "dynamic_per_report_company_lang":
            custom_background = self._get_background_per_report_company_language()
            return custom_background
        # If custom_report_type is report then set report(self) id.
        if self.custom_report_type == "report":
            custom_bg_from = self
        # If custom_report_type is company then set current company id from context.
        if self.custom_report_type == "company" or not self.custom_report_type:
            custom_bg_from = company_background

        # Filter records from report_background_lang model based on the languages.
        # custom_bg_from: company_id or report_id(self).
        custom_bg_lang = custom_bg_from.bg_per_lang_ids.filtered(
            lambda lang: lang.lang_id.code == lang_code
        )

        # Set 1st custom background.
        custom_background = custom_bg_lang[:1].background_pdf
        return custom_background

    def _dynamic_background_per_report(self, report, pdf_report_path):  # noqa: C901
        """Dynamic Type and Background Per Report - Company - Lang #T5886"""
        lang_domain = []
        if (
            report
            and report.custom_report_background
            and report.custom_report_type
            in ["dynamic", "dynamic_per_report_company_lang"]
        ):
            temp_report_id, temp_report_path = tempfile.mkstemp(
                suffix=".pdf", prefix="with_back_report.tmp."
            )
            output = PdfFileWriter()
            pdf_reader_content = PdfFileReader(pdf_report_path, "rb")

            # Call method for get domain related to the languages. #22260
            lang_domain = report.with_context(**self.env.context).get_bg_per_lang()

            first_page = last_page = fixed_page = remaining_pages = expression = False
            if report.custom_report_type == "dynamic":
                # Added lang_domain in all search methods. #22260
                first_page = report.background_ids.search(
                    lang_domain
                    + [
                        ("type", "=", "first_page"),
                        ("report_id", "=", report.id),
                    ],
                    limit=1,
                )
                last_page = report.background_ids.search(
                    lang_domain
                    + [
                        ("type", "=", "last_page"),
                        ("report_id", "=", report.id),
                    ],
                    limit=1,
                )
                fixed_pages = report.background_ids.search(
                    lang_domain
                    + [
                        ("type", "=", "fixed"),
                        ("report_id", "=", report.id),
                    ]
                )
                remaining_pages = report.background_ids.search(
                    lang_domain
                    + [
                        ("type", "=", "remaining"),
                        ("report_id", "=", report.id),
                    ],
                    limit=1,
                )
                expression = report.background_ids.search(
                    lang_domain
                    + [
                        ("type", "=", "expression"),
                        ("report_id", "=", report.id),
                    ],
                    limit=1,
                )

            company_background = self._context.get("background_company")
            company_background_img = company_background.custom_report_background_image
            # Start. #22260
            if report.is_bg_per_lang:
                lang_code = report.get_lang()
                custom_bg_lang = company_background.bg_per_lang_ids.filtered(
                    lambda lang: lang.lang_id.code == lang_code
                )
            # End. #22260
            for i in range(pdf_reader_content.getNumPages()):
                watermark = ""
                if report.custom_report_type == "dynamic_per_report_company_lang":
                    watermark = lang_domain
                elif first_page and i == 0:
                    if first_page.fall_back_to_company and company_background:
                        # Start. #22260
                        # If is_bg_per_lang then get custom bg from the company.
                        if report.is_bg_per_lang:
                            watermark = custom_bg_lang[:1].background_pdf
                        else:
                            watermark = company_background_img
                        # End. #22260
                    # Fix page 1st issue. #22260
                    elif first_page.background_pdf:
                        watermark = first_page.background_pdf
                elif last_page and i == pdf_reader_content.getNumPages() - 1:
                    if last_page.fall_back_to_company and company_background:
                        # Start. #22260
                        # If is_bg_per_lang then get custom bg from the company.
                        if report.is_bg_per_lang:
                            watermark = custom_bg_lang[:1].background_pdf
                        else:
                            watermark = company_background_img
                        # End. #22260
                    elif last_page.background_pdf:
                        watermark = last_page.background_pdf
                elif i + 1 in fixed_pages.mapped("page_number"):
                    fixed_page = fixed_pages.search(
                        [
                            ("page_number", "=", i + 1),
                            ("report_id", "=", report.id),
                        ],
                        limit=1,
                    )
                    if (
                        fixed_page
                        and fixed_page.fall_back_to_company
                        and company_background
                    ):
                        # Start. #22260
                        # If is_bg_per_lang then get custom bg from the company.
                        if report.is_bg_per_lang:
                            watermark = custom_bg_lang[:1].background_pdf
                        else:
                            watermark = company_background_img
                        # End. #22260
                    elif fixed_page and fixed_page.background_pdf:
                        watermark = fixed_page.background_pdf
                elif expression and expression.page_expression:
                    eval_dict = {"page": i + 1}
                    safe_eval(
                        expression.page_expression,
                        eval_dict,
                        mode="exec",
                        nocopy=True,
                    )
                    if (
                        expression.fall_back_to_company
                        and company_background
                        and eval_dict.get("result", False)
                    ):
                        # Start. #22260
                        # If is_bg_per_lang then get custom bg from the company.
                        if report.is_bg_per_lang:
                            watermark = custom_bg_lang[:1].background_pdf
                        else:
                            watermark = company_background_img
                        # End. #22260
                    elif eval_dict.get("result", False) and expression.background_pdf:
                        watermark = expression.background_pdf
                    else:
                        if remaining_pages:
                            if (
                                remaining_pages.fall_back_to_company
                                and company_background
                            ):
                                # Start. #22260
                                # If is_bg_per_lang then get
                                # custom bg from the company.
                                if report.is_bg_per_lang:
                                    watermark = custom_bg_lang[:1].background_pdf
                                else:
                                    watermark = company_background_img
                                # End. #22260
                            elif remaining_pages.background_pdf:
                                watermark = remaining_pages.background_pdf
                else:
                    if remaining_pages:
                        if remaining_pages.fall_back_to_company and company_background:
                            # Start. #22260
                            # If is_bg_per_lang then get custom bg from the company.
                            if report.is_bg_per_lang:
                                watermark = custom_bg_lang[:1].background_pdf
                            else:
                                watermark = company_background_img
                            # End. #22260
                        elif remaining_pages.background_pdf:
                            watermark = remaining_pages.background_pdf
                if watermark:
                    page = report.add_pdf_watermarks(
                        watermark,
                        pdf_reader_content.getPage(i),
                    )
                else:
                    page = pdf_reader_content.getPage(i)
                output.addPage(page)
            output.write(open(temp_report_path, "wb"))
            pdf_report_path = temp_report_path
            os.close(temp_report_id)
        elif report.custom_report_background:
            temp_back_id, temp_back_path = tempfile.mkstemp(
                suffix=".pdf", prefix="back_report.tmp."
            )
            custom_background = False
            # From Report Type.
            if (
                report
                and report.custom_report_background
                and report.custom_report_type == "report"
            ):
                # 222760 Starts.If background per lang is True then call method for
                # get custom background based on different languages.
                if report.is_bg_per_lang:
                    custom_background = report.with_context(
                        **self.env.context
                    ).get_bg_per_lang()
                # 222760 Ends.
                else:
                    custom_background = report.custom_report_background_image
                # 222760 Ends.
            # From Company Type.
            if (
                report.custom_report_background
                and not custom_background
                and (
                    report.custom_report_type == "company"
                    or not report.custom_report_type
                )
                and self._context.get("background_company")  # #19896
            ):
                # report background will be displayed based on the current
                # company #19896
                company_id = self._context.get("background_company")
                # 222760 Starts. If background per lang is True then call method for
                # get custom background from company based on different languages.
                if report.is_bg_per_lang:
                    custom_background = report.with_context(
                        **self.env.context
                    ).get_bg_per_lang()
                # 222760 Ends.
                else:
                    custom_background = company_id.custom_report_background_image
            # If background found from any type then set that to the report.
            if custom_background:
                back_data = base64.b64decode(custom_background)
                with closing(os.fdopen(temp_back_id, "wb")) as back_file:
                    back_file.write(back_data)
                temp_report_id, temp_report_path = tempfile.mkstemp(
                    suffix=".pdf", prefix="with_back_report.tmp."
                )
                output = PdfFileWriter()
                pdf_reader_content = PdfFileReader(pdf_report_path, "rb")

                for i in range(pdf_reader_content.getNumPages()):
                    page = pdf_reader_content.getPage(i)
                    pdf_reader_watermark = PdfFileReader(temp_back_path, "rb")
                    watermark = pdf_reader_watermark.getPage(0)
                    watermark.mergePage(page)
                    output.addPage(watermark)
                output.write(open(temp_report_path, "wb"))
                pdf_report_path = temp_report_path
                os.close(temp_report_id)
        return lang_domain, pdf_report_path

    @api.model
    def _run_wkhtmltopdf(  # noqa: C901
        self,
        bodies,
        report_ref=False,
        header=None,
        footer=None,
        landscape=False,
        specific_paperformat_args=None,
        set_viewport_size=False,
    ):
        """
        Override Method : Execute wkhtmltopdf as a subprocess in order to
        convert html given in input into a pdf document.

        :param bodies: The html bodies of the report, one per page.
        :param header: The html header of the report containing all headers.
        :param footer: The html footer of the report containing all footers.
        :param landscape: Force the pdf to be rendered under a landscape
                        format.
        :param specific_paperformat_args: dict of prioritized paperformat
                                        arguments.
        :param set_viewport_size: Enable a viewport sized '1024x1280' or
                                '1280x1024' depending of landscape arg.
        :return: Content of the pdf as a string
        """
        # call default odoo standard function of paperformat #19896
        # https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/models
        # /ir_actions_report.py#L243
        paperformat_id = (
            self._get_report(report_ref).get_paperformat()
            if report_ref
            else self.get_paperformat()
        )
        report = self._get_report(report_ref)
        # Build the base command args for wkhtmltopdf bin
        command_args = self._build_wkhtmltopdf_args(
            paperformat_id,
            landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )

        files_command_args = []
        temporary_files = []
        if header:
            head_file_fd, head_file_path = tempfile.mkstemp(
                suffix=".html", prefix="report.header.tmp."
            )
            with closing(os.fdopen(head_file_fd, "wb")) as head_file:
                head_file.write(header.encode())
            temporary_files.append(head_file_path)
            files_command_args.extend(["--header-html", head_file_path])
        if footer:
            foot_file_fd, foot_file_path = tempfile.mkstemp(
                suffix=".html", prefix="report.footer.tmp."
            )
            with closing(os.fdopen(foot_file_fd, "wb")) as foot_file:
                foot_file.write(footer.encode())
            temporary_files.append(foot_file_path)
            files_command_args.extend(["--footer-html", foot_file_path])

        paths = []
        for i, body in enumerate(bodies):
            prefix = "%s%d." % ("report.body.tmp.", i)
            body_file_fd, body_file_path = tempfile.mkstemp(
                suffix=".html", prefix=prefix
            )
            with closing(os.fdopen(body_file_fd, "wb")) as body_file:
                # HACK: wkhtmltopdf doesn't like big table at all and the
                #       processing time become exponential with the number
                #       of rows (like 1H for 250k rows).
                #
                #       So we split the table into multiple tables containing
                #       500 rows each. This reduce the processing time to 1min
                #       for 250k rows. The number 500 was taken from opw-1689673
                if len(body) < 4 * 1024 * 1024:  # 4Mib
                    body_file.write(body.encode())
                else:
                    tree = lxml.html.fromstring(body)
                    _split_table(tree, 500)
                    body_file.write(lxml.html.tostring(tree))
            paths.append(body_file_path)
            temporary_files.append(body_file_path)

        pdf_report_fd, pdf_report_path = tempfile.mkstemp(
            suffix=".pdf", prefix="report.tmp."
        )
        os.close(pdf_report_fd)
        temporary_files.append(pdf_report_path)
        try:
            wkhtmltopdf = (
                [_get_wkhtmltopdf_bin()]
                + command_args
                + files_command_args
                + paths
                + [pdf_report_path]
            )
            process = subprocess.Popen(
                wkhtmltopdf, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            out, err = process.communicate()
            err = ustr(err)

            if process.returncode not in [0, 1]:
                if process.returncode == -11:
                    message = (
                        "Wkhtmltopdf failed (error code: %s). Memory limit "
                        "too low or "
                        "maximum file number of subprocess reached. Message : %s"
                    )
                else:
                    message = "Wkhtmltopdf failed (error code: %s). Message: %s"
                _logger.warning(message, process.returncode, err[-1000:])
                raise UserError(message % (str(process.returncode), err[-1000:]))
            else:
                if err:
                    _logger.warning("wkhtmltopdf: %s" % err)
            # BAD-CUSTOMIZATION START
            lang_domain, pdf_report_path = self._dynamic_background_per_report(
                report=report, pdf_report_path=pdf_report_path
            )
            # BAD-CUSTOMIZATION END

        except Exception as ex:
            logging.info("Error while PDF Background %s" % ex)
            raise

        with open(pdf_report_path, "rb") as pdf_document:
            pdf_content = pdf_document.read()

        # BAD Customization start. T6622
        if (
            report
            and report.custom_report_background
            and report.custom_report_type
            in ["dynamic", "dynamic_per_report_company_lang"]
        ):
            if report.custom_report_type == "dynamic":
                # search append attachment record. #T6622
                append_attachment = report.background_ids.search(
                    lang_domain
                    + [
                        ("type", "=", "append"),
                        ("report_id", "=", report.id),
                    ],
                )
                # search prepend attachment record. #T6622
                prepend_attachment = report.background_ids.search(
                    lang_domain
                    + [
                        ("type", "=", "prepend"),
                        ("report_id", "=", report.id),
                    ],
                )
            if report.custom_report_type == "dynamic_per_report_company_lang":
                lang_domain = [("background_pdf", "!=", False)]
                # search append attachment record. #T6622
                append_attachment = report.per_report_com_lang_bg_ids.search(
                    lang_domain
                    + [
                        ("type_attachment", "=", "append"),
                        ("report_id", "=", report.id),
                    ],
                )
                # search prepend attachment record. #T6622
                prepend_attachment = report.per_report_com_lang_bg_ids.search(
                    lang_domain
                    + [
                        ("type_attachment", "=", "prepend"),
                        ("report_id", "=", report.id),
                    ],
                )
            data = []

            # Merge multiple prepend attachment. #T6622
            for prepend_data in prepend_attachment:
                if prepend_data and prepend_data.background_pdf:
                    data.append(base64.b64decode(prepend_data.background_pdf))

            data.append(pdf_content)

            # Merge multiple append attachment. #T6622
            for append_data in append_attachment:
                if append_data and append_data.background_pdf:
                    data.append(base64.b64decode(append_data.background_pdf))

            # call function for merge pdf reports and attachments. #T6622
            pdf_content = pdf.merge_pdf(data)

        # Manual cleanup of the temporary files
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except (OSError, IOError):  # noqa: B014
                _logger.error("Error when trying to remove file %s" % temporary_file)

        return pdf_content
