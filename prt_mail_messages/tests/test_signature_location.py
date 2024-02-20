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

from odoo.tests import Form, tagged
from odoo.tools import mute_logger

from odoo.addons.test_mail.tests.test_mail_composer import TestMailComposer


@tagged("post_install", "-at_install", "test_signature_location")
class TestSignatureLocation(TestMailComposer):
    @classmethod
    def setUpClass(cls):
        super(TestMailComposer, cls).setUpClass()
        # Create Partner Kate
        cls.kate = cls.env["res.partner"].create(
            {"name": "Kate", "email": "kate@example.com"}
        )
        # Mail Message Test #1
        cls.mail_message_test_1 = cls.env["mail.message"].create(
            {
                "model": cls.kate._name,
                "res_id": cls.kate.id,
                "body": "Test Message #1",
            }
        )

    def get_message(self, location):
        """Get the last message created with signature location"""
        self.env["ir.config_parameter"].sudo().set_param(
            "cetmix.message_signature_location", location
        )
        compose_form = Form(
            self.env["mail.compose.message"].with_context(
                **self.mail_message_test_1.with_context(
                    wizard_mode="quote"
                ).reply_prep_context(),
            )
        )
        compose_form.partner_ids.add(self.kate)
        composer = compose_form.save()
        with self.mock_mail_gateway(mail_unlink_sent=False):
            composer._action_send_mail()
        return self.kate.message_ids[0]

    @mute_logger("odoo.tests", "odoo.addons.mail.models.mail_mail")
    def test_mail_composer_signature_bottom_or_default(self):
        """Test signature location bottom/default"""
        message = self.get_message("a")
        signature = message.create_uid.signature
        body = message.mail_ids.body_html
        start_quote = body.find("<blockquote")
        self.assertNotIn(
            signature,
            body[:start_quote],
            msg="Signature must not be before block <blockquote>",
        )
        end_quote = body.find("</blockquote>")
        self.assertIn(
            signature,
            body[end_quote:],
            msg="Signature must be after block </blockquote>",
        )

    @mute_logger("odoo.tests", "odoo.addons.mail.models.mail_mail")
    def test_mail_composer_signature_before(self):
        """Test signature location before quote"""
        message = self.get_message("b")
        signature = message.create_uid.signature
        body = message.mail_ids.body_html
        start_quote = body.find("<blockquote")
        self.assertIn(
            signature,
            body[:start_quote],
            msg="Signature must be before block <blockquote>",
        )
        end_quote = body.find("</blockquote>")
        self.assertNotIn(
            signature,
            body[end_quote:],
            msg="Signature must not be after block </blockquote>",
        )

    @mute_logger("odoo.tests", "odoo.addons.mail.models.mail_mail")
    def test_mail_composer_no_signature(self):
        """Test without signature location"""
        message = self.get_message("n")
        signature = message.create_uid.signature
        body = message.mail_ids.body_html
        self.assertNotIn(
            signature, body, msg="Signature must not contains in message body"
        )
