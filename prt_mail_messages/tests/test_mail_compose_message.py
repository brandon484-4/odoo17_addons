###################################################################################
#
#    Copyright (C) 2020 Cetmix OÜ
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

import re

from lxml.html import fromstring

from odoo.tests import Form
from odoo.tools import misc

from .common import MailMessageCommon


class TestMailComposeMessage(MailMessageCommon):
    """
    TEST 1 : Check valid fields value in forward mode
    TEST 2 : Check behavior get_record_data function
    TEST 3 : Check preparing partners by parent mail message record
    TEST 4 : Check default signature location
    """

    # -- TEST 1 : Check valid fields value in forward mode
    def test_valid_forward_reference(self):
        """Check field values in forward mode"""

        # 'compose' mode
        # as if the "mail" button is clicked on Partner form
        with Form(
            self.env["mail.compose.message"].with_context(
                default_wizard_mode="compose",
                default_model="res.partner",
                default_res_id=self.res_partner_kate.id,
            )
        ) as form:
            self.assertEqual(
                form.forward_ref,
                f"res.partner,{self.res_partner_kate.id}",
                f"Reference must be set to {self.res_partner_kate.name}",
            )

    # -- TEST 2 : Check behavior get_record_data function
    def test_compose_message_record_data(self):
        """Check behavior of the get_record_data function"""
        record_data = (
            self.env["mail.compose.message"]
            .with_context(default_subject="Custom Subject")
            .get_record_data({})
        )
        keys = list(record_data.keys())
        self.assertListEqual(keys, ["subject"], msg="Keys must be the same")
        self.assertEqual(
            record_data.get("subject"),
            "Custom Subject",
            msg="Subject value must be equal to 'Custom Subject'",
        )
        record_data = self.env["mail.compose.message"].get_record_data(
            {"parent_id": self.mail_message_parent.id}
        )
        keys = list(record_data.keys())
        self.assertListEqual(
            keys,
            ["record_name", "model", "res_id", "partner_ids", "subject"],
            msg="Keys must be the same",
        )
        self.assertEqual(
            record_data.get("record_name"),
            "Kate",
            msg="Record Name must be equal to 'Kate'",
        )
        self.assertListEqual(
            record_data.get("partner_ids"),
            [(4, self.res_partner_kate.id), (4, self.res_partner_mark.id)],
            msg="Partners must be the same",
        )
        self.assertEqual(
            record_data.get("model"),
            "res.partner",
            msg="Model must be equal to 'res.partner'",
        )
        self.assertEqual(
            record_data.get("res_id"),
            self.res_partner_kate.id,
            msg=f"Res ID must be equal to {self.res_partner_kate.id}",
        )
        self.assertEqual(
            record_data.get("subject"),
            "Re: Kate",
            msg="Subject value must be equal to 'Re: Kate'",
        )
        record_data = self.env["mail.compose.message"].get_record_data(
            {"model": "res.partner", "res_id": self.res_partner_kate.id}
        )
        keys = list(record_data.keys())
        self.assertListEqual(
            keys, ["record_name", "subject"], msg="Keys must be the same"
        )
        record_data = (
            self.env["mail.compose.message"]
            .with_context(default_wizard_mode="forward")
            .get_record_data(
                {"model": "res.partner", "res_id": self.res_partner_kate.id}
            )
        )
        keys = list(record_data.keys())
        self.assertListEqual(
            keys, ["record_name", "subject"], msg="Keys must be the same"
        )
        self.assertEqual(
            record_data.get("subject"),
            "Fwd: Kate",
            msg="Subject value must be equal to 'Fwd: Kate'",
        )

    # -- TEST 3 : Check preparing partners by parent mail message record
    def test_prepare_valid_record_partners(self):
        """Check preparing partners by parent mail message record"""
        parent = self.mail_message_parent
        MailCompose = self.env["mail.compose.message"]
        partner_ids = MailCompose._prepare_valid_record_partners(parent, [])
        partners = [(4, self.res_partner_kate.id), (4, self.res_partner_mark.id)]
        self.assertListEqual(partner_ids, partners, msg="Partners must be the same")
        partner_ids = MailCompose._prepare_valid_record_partners(
            parent, [(6, 0, self.res_partner_kate.ids)]
        )
        self.assertListEqual(
            partner_ids,
            [(6, 0, self.res_partner_kate.ids)] + partners,
            msg="Partners must be the same",
        )
        partner_ids = MailCompose.with_context(
            is_private=True
        )._prepare_valid_record_partners(parent, [])
        self.assertListEqual(
            partner_ids,
            partners + [(4, self.res_partner_ann.id)],
            msg="Partners must be the same",
        )

    # -- TEST 4 : Check default signature location
    def test_default_signature_location(self):
        """Check default signature location"""
        MailCompose = self.env["mail.compose.message"]
        ICPSudo = self.env["ir.config_parameter"].sudo()

        ICPSudo.set_param("cetmix.message_signature_location", "a")
        self.assertEqual(
            MailCompose._default_signature_location(),
            "a",
            msg="Default signature location must be equal to 'a' (Message bottom)",
        )
        ICPSudo.set_param("cetmix.message_signature_location", "b")
        self.assertEqual(
            MailCompose._default_signature_location(),
            "b",
            msg="Default signature location must be equal to 'a' (Before quote)",
        )
        ICPSudo.set_param("cetmix.message_signature_location", "n")
        self.assertEqual(
            MailCompose._default_signature_location(),
            "n",
            msg="Default signature location must be equal to 'n' (No signature)",
        )

    # -- TEST 5 : Test flow that prepared value for message quotation in composer
    def test_mail_compose_message_default_get_quote(self):
        """Test flow that prepared value for message quotation in composer"""
        parent = self.mail_message_parent
        context = parent.with_context(wizard_mode="quote").reply_prep_context()
        self.assertEqual(
            context.get("default_parent_id"),
            parent.id,
            f"'default_parent_id' must be equal to {parent.id}",
        )
        self.assertEqual(
            context.get("default_wizard_mode"),
            "quote",
            "'default_wizard_mode' must be equal to 'quote'",
        )

        composer = self.env["mail.compose.message"].with_context(**context).create({})
        self.assertIn("<blockquote", composer.body, "Body must contain the quote block")
        self.assertEqual(
            composer.wizard_mode, "quote", "Wizard mode value must be equal to 'quote'"
        )

    # -- TEST 6 : Test flow that prepared value for message forward in composer
    def test_mail_compose_message_default_get_forward(self):
        """Test flow that prepared value for message forward in composer"""
        parent = self.mail_message_parent
        context = parent.with_context(wizard_mode="forward").reply_prep_context()
        self.assertEqual(
            context.get("default_parent_id"),
            parent.id,
            f"'default_parent_id' must be equal to {parent.id}",
        )
        self.assertEqual(
            context.get("default_wizard_mode"),
            "forward",
            "'default_wizard_mode' must be equal to 'quote'",
        )

        composer = self.env["mail.compose.message"].with_context(**context).create({})
        self.assertFalse(composer.parent_id, msg="parent_id must be False")
        self.assertIn("<blockquote", composer.body, "Body must contain the quote block")

    # -- TEST 7 : Test flow that prepared quoted body
    def test_prepare_quoted_body(self):
        """Test flow when prepared quoted body"""
        parent = self.mail_message_parent
        parent.subject = "Test Subject"
        body = self.env["mail.compose.message"]._prepare_quoted_body(parent, True)

        date = misc.format_datetime(self.env, parent.date)
        match = re.search("Date: (.+?) <br/>", body)
        found = match.group(1)
        self.assertEqual(found, date, f"Date value must be equal to {date}")

        match = re.search("From: (.+?) <br/>", body)
        found = match.group(1)
        self.assertEqual(
            found,
            str(parent.author_display),
            f"From value must be equal to {parent.author_display}",
        )

        match = re.search("Subject: (.+?) <br/>", body)
        found = match.group(1)
        self.assertEqual(
            found,
            str(parent.subject),
            f"Subject value must be equal to {parent.subject}",
        )

    # -- TEST 8 : Test flow that trim block quote from message body
    def test_trim_quote_blocks(self):
        """Test flow that trim block quote from message body"""
        message_body = """<p style='margin:0px 0px 9px 0px; font-size:13px; font-family:"Lucida Grande", Helvetica, Verdana, Arial, sans-serif'>Test Message #3</p><br><blockquote style="border-style:none none none solid; padding:9px 18px 9px 18px; margin:0px 0px 18px 0px; border-left-color:rgb(249, 249, 249); border-left-width:5px; font-size:16.25px" data-o-mail-quote="1">----- Original message ----- <br> Date: 2023-11-25 16:47:30 <br> From: Administrator <br> Subject: Re: Fwd: Agrolait <br><br><p style='margin:0px 0px 9px 0px; font-size:13px; font-family:"Lucida Grande", Helvetica, Verdana, Arial, sans-serif'>Test Message #2</p><hr style="border-style:solid none none none; margin:18px 0 18px 0; border-top-color:rgb(249, 249, 249); border-top-width:1px; border-left-color:currentcolor; border-left-width:0px; border-bottom-color:currentcolor; border-bottom-width:0px; border-right-color:currentcolor; border-right-width:0px; height:0px"><br><br><blockquote style="border-style:none none none solid; padding:9px 18px 9px 18px; margin:0px 0px 18px 0px; border-left-color:rgb(249, 249, 249); border-left-width:5px; font-size:16.25px" data-o-mail-quote="1">----- Original message ----- <br> Date: 2023-11-25 16:47:11 <br> From: Administrator <br> Subject: Re: Fwd: Agrolait <br><br><p style='margin:0px 0px 9px 0px; font-size:13px; font-family:"Lucida Grande", Helvetica, Verdana, Arial, sans-serif'></p><p style='margin:0px 0px 9px 0px; font-size:13px; font-family:"Lucida Grande", Helvetica, Verdana, Arial, sans-serif'>Test Message #1</p><hr style="border-style:solid none none none; margin:18px 0 18px 0; border-top-color:rgb(249, 249, 249); border-top-width:1px; border-left-color:currentcolor; border-left-width:0px; border-bottom-color:currentcolor; border-bottom-width:0px; border-right-color:currentcolor; border-right-width:0px; height:0px"><br><blockquote style="border-style:none none none solid; padding:9px 18px 9px 18px; margin:0px 0px 18px 0px; border-left-color:rgb(249, 249, 249); border-left-width:5px; font-size:16.25px" data-o-mail-quote="1">----- Original message ----- <br> Date: 2023-11-19 15:40:37 <br> From: Administrator <br> Subject: Fwd: Agrolait <br><br><p style='margin:0px 0px 9px 0px; font-size:13px; font-family:"Lucida Grande", Helvetica, Verdana, Arial, sans-serif'>TEST<br></p><br><blockquote style="border-style:none none none solid; padding:9px 18px 9px 18px; margin:0px 0px 18px 0px; border-left-color:rgb(249, 249, 249); border-left-width:5px; font-size:16.25px" data-o-mail-quote="1">----- Original message ----- <br> Date: 11/16/2023 20:03:46 <br> From: Administrator <br> Subject: Re: Agrolait <br><br><p style='margin:0px; font-size:13px; font-family:"Lucida Grande", Helvetica, Verdana, Arial, sans-serif'>TESTSET<br></p></blockquote></blockquote></blockquote></blockquote>"""  # noqa
        expected_body = "<p>Hello World</p>"
        body = self.env["mail.compose.message"]._trim_quote_blocks(expected_body, 0)
        self.assertEqual(body, expected_body, "Values must be the same")

        expected_body = "<p>Hello World</p>"
        body = self.env["mail.compose.message"]._trim_quote_blocks(expected_body, 1)
        self.assertEqual(body, expected_body, "Values must be the same")

        body = self.env["mail.compose.message"]._trim_quote_blocks(message_body, 10)
        self.assertEqual(body, message_body, "Values must be the same")

        tree = fromstring(message_body)
        expected_blocks = tree.xpath("//blockquote")
        self.assertEqual(len(expected_blocks), 4, "Blocks count must be equal to 4")

        body = self.env["mail.compose.message"]._trim_quote_blocks(message_body, 0)
        tree = fromstring(body)
        blocks = tree.xpath("//blockquote")
        self.assertEqual(
            len(blocks), len(expected_blocks), "Blocks count must be the same"
        )

        body = self.env["mail.compose.message"]._trim_quote_blocks(message_body, 4)
        tree = fromstring(body)
        blocks = tree.xpath("//blockquote")
        self.assertEqual(
            len(blocks), len(expected_blocks), "Blocks count must be the same"
        )

        body = self.env["mail.compose.message"]._trim_quote_blocks(message_body, 3)
        tree = fromstring(body)
        blocks = tree.xpath("//blockquote")
        self.assertEqual(len(blocks), 3, "Blocks count must be equal to 3")

        body = self.env["mail.compose.message"]._trim_quote_blocks(message_body, 1)
        tree = fromstring(body)
        blocks = tree.xpath("//blockquote")
        self.assertEqual(len(blocks), 1, "Blocks count must be equal to 1")
