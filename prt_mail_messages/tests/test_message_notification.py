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

from email.message import EmailMessage

from odoo.tests import tagged

from .common import MailMessageCommon


@tagged("post_install", "-at_install")
class TestMessageNotification(MailMessageCommon):
    """
    TEST 1 : Notify partners on incoming message
        - Set True config parameter 'mail_incoming_smart_notify'
        - Processing incoming message
        - Get sent mail message
        - Mail messages count: 2
        - Mail messages #1 recipients: Partner "Demo Notification Type Email"
        - Mail messages #2 recipients count: 2
        - Mail messages #2 recipients: Bob and Mark
    """

    def setUp(self):
        super().setUp()

        def unlink_replacement(self):
            return

        self.env["mail.mail"]._patch_method("unlink", unlink_replacement)

        partner_ids = [
            self.res_partner_kate.id,
            self.res_partner_ann.id,
            self.res_partner_bob.id,
            self.res_partner_mark.id,
            self.res_users_internal_user_email.partner_id.id,
            self.res_users_internal_user_odoo.partner_id.id,
        ]

        self.res_partner_target_record.message_subscribe(partner_ids, [])

        self.message_dict = {
            "message_type": "email",
            "message_id": "<CAFkrrMwZJvtNe6kEM538Xu99TmCn=BgwaLMRMPi+otCSO4G6BQ@mail.example.com>",  # noqa
            "subject": "Test Subject",
            "from": "Mark <mark@example.com>",
            "to": f"{self.res_partner_kate.name} <{self.res_partner_kate.email}>, {self.res_partner_ann.name} <{self.res_partner_ann.email}>",  # noqa
            "cc": "",
            "references": "",
            "email_from": "Mark <mark@exmaple.com>",
            "recipients": "test_example@example.com",
            "in_reply_to": """<CABFLKG=gJvxLSEgJNcPowcyo-cuJKoc3vuYv+coCC63qmfqo6A@example.com>""",  # noqa
            "partner_ids": [self.res_partner_kate.id, self.res_partner_ann.id],
            "date": "2022-06-23 16:52:15",
            "internal": False,
            "body": "",
            "attachments": [],
            "author_id": False,
        }

        # Monkey patch to keep sent mails for further check
        def unlink_replacement(self):
            return

        self.env["mail.mail"]._patch_method("unlink", unlink_replacement)

    # -- TEST 1 : Notify partners on incoming message
    def test_message_route_process(self):
        """Notify partners on incoming message"""

        # Set True config parameter 'mail_incoming_smart_notify'
        # Processing incoming message
        # Get sent mail message
        # Mail messages count: 2
        # Mail messages #1 recipients: Partner "Demo Notification Type Email"
        # Mail messages #2 recipients count: 2
        # Mail messages #2 recipients: Bob and Mark
        IrConfig = self.env["ir.config_parameter"].sudo()
        key = "cetmix.mail_incoming_smart_notify"

        IrConfig.set_param(key, True)
        self.assertTrue(IrConfig.get_param(key), msg="Result must be True")

        target = self.res_partner_target_record
        user_id = self.env.user.id
        routes = [(target._name, target.id, None, user_id, None)]
        self.env["mail.thread"]._message_route_process("", self.message_dict, routes)
        mail_ids = self.env["mail.mail"].search(
            [
                ("res_id", "=", target.id),
                ("model", "=", target._name),
            ]
        )
        self.assertEqual(len(mail_ids), 2, msg="Mail Messages count must be equal 2")

        internal_partner_mail = mail_ids.filtered(
            lambda mail: len(mail.recipient_ids) == 1
        )

        self.assertEqual(
            internal_partner_mail.recipient_ids,
            self.res_users_internal_user_email.partner_id,
            msg="Mail recipient must be equal only "
            "internal partner (notification type == Email)",
        )

        partner_mail = mail_ids.filtered(
            lambda mail: mail.id != internal_partner_mail.id
        )

        self.assertNotIn(
            self.res_users_internal_user_email.partner_id.id,
            partner_mail.recipient_ids.ids,
            msg="Message recipients must contain internal partner (odoo)",
        )
        self.assertIn(
            self.res_partner_bob.id,
            partner_mail.recipient_ids.ids,
            msg="Message recipients must contain partner Bob",
        )
        self.assertIn(
            self.res_partner_mark.id,
            partner_mail.recipient_ids.ids,
            msg="Message recipients must contain partner Mark",
        )

    def test_message_route_allow_direct_message(self):
        """
        Test flow that check using 'allow direct' config for message_route method.

        - Checking method behavior with deactivate
        'allow direct' config (by default behavior)
        - Checking method behavior with set 'allow direct' config.
        """
        msg = EmailMessage()
        msg["To"] = ""
        msg["subject"] = "---Test---"
        self.message_dict.update(
            to=f"{self.res_partner_kate.name} <{self.res_partner_kate.email}>"
        )
        self.env["ir.config_parameter"].sudo().set_param("mail.catchall.alias", "kate")
        self.env["ir.config_parameter"].sudo().set_param(
            "mail.catchall.domain", "test-example.com"
        )
        self.env["ir.config_parameter"].sudo().set_param(
            "mail.default.from", "test@custom_domain.com"
        )

        # Default behavior
        # Allow direct message to catchall is false
        result = self.env["mail.thread"].message_route(msg, self.message_dict)
        self.assertEqual(result, [])
        # Find created message after message_route method
        mail = self.env["mail.mail"].search([("subject", "=", "Re: ---Test---")])
        self.assertEqual(len(mail), 1)

        # Active Allow Direct behavior
        # Allow direct message to catchall set True
        self.env["ir.config_parameter"].sudo().set_param(
            "cetmix.allow_direct_messages_to_catchall", True
        )
        # ValueError if no routes found and if no bounce occurred
        with self.assertRaises(ValueError):
            self.env["mail.thread"].message_route(msg, self.message_dict)
