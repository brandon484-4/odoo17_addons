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

from odoo.tests import TransactionCase


class MailMessageCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ResPartner = cls.env["res.partner"]
        MailMessage = cls.env["mail.message"]
        ResUsers = cls.env["res.users"].with_context(mail_create_nolog=True)

        group_user_id = cls.env.ref("base.group_user").id
        cls.cx_model_reference_partner = cls.env.ref(
            "prt_mail_messages.cx_model_reference_res_partner"
        )
        cls.res_partner_kate = ResPartner.create(
            {"name": "Kate", "email": "kate@example.com"}
        )
        cls.res_partner_ann = ResPartner.create(
            {"name": "Ann", "email": "ann@example.com"}
        )
        cls.res_partner_bob = ResPartner.create(
            {"name": "Bob", "email": "bob@example.com"}
        )
        cls.res_partner_mark = ResPartner.create(
            {"name": "Mark", "email": "mark@example.com"}
        )
        cls.res_partner_target_record = ResPartner.create(
            {"name": "Target", "email": "target@example.com"}
        )

        cls.test_user = ResUsers.create(
            {
                "name": "Test User #1",
                "login": "test_user",
                "email": "testuser1@example.com",
                "groups_id": [(4, group_user_id)],
            }
        )
        cls.res_users_internal_user_email = ResUsers.create(
            {
                "name": "Demo Notification Type Email",
                "login": "demo_email",
                "email": "demo.email@example.com",
                "groups_id": [(4, group_user_id)],
                "notification_type": "email",
            }
        )

        cls.res_users_internal_user_odoo = ResUsers.create(
            {
                "name": "Demo Notification Type Odoo",
                "login": "demo_odoo",
                "email": "demo.odoo@exmaple.com",
                "groups_id": [(4, group_user_id)],
                "notification_type": "inbox",
            }
        )

        cls.mail_message_parent = MailMessage.create(
            {
                "author_id": cls.res_partner_ann.id,
                "author_allowed_id": cls.res_partner_kate.id,
                "body": "Test Body Parent",
                "partner_ids": [
                    (4, cls.env.user.partner_id.id),
                    (4, cls.res_partner_kate.id),
                    (4, cls.res_partner_mark.id),
                ],
                "res_id": cls.res_partner_kate.id,
                "model": cls.res_partner_kate._name,
            }
        )

        cls.mail_message_test_1 = MailMessage.create(
            {
                "author_id": cls.res_partner_ann.id,
                "author_allowed_id": cls.res_partner_kate.id,
                "body": "Test Body Child",
                "partner_ids": [],
                "parent_id": cls.mail_message_parent.id,
                "res_id": cls.res_partner_kate.id,
                "model": cls.res_partner_kate._name,
            }
        )

        cls.cetmix_conversation_1 = cls.env.ref(
            "prt_mail_messages.cetmix_conversation_test_1"
        )

        cls.mail_message_test_conversation = MailMessage.create(
            {
                "author_id": cls.res_partner_ann.id,
                "author_allowed_id": cls.res_partner_kate.id,
                "body": "Test Body Child",
                "partner_ids": [],
                "parent_id": cls.mail_message_parent.id,
                "res_id": cls.cetmix_conversation_1.id,
                "model": "cetmix.conversation",
            }
        )
