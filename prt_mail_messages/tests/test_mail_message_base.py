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

from .common import MailMessageCommon


class TestMailMessageBase(MailMessageCommon):
    def setUp(self):
        super().setUp()

    def test_get_mail_thread_data_res_partner(self):
        """Test flow get thread data for `res.partner` record"""
        result = self.res_partner_ann._get_mail_thread_data([])
        self.assertTrue(result.get("hasWriteAccess"))
        self.assertTrue(result.get("hasReadAccess"))
        self.assertFalse(result.get("canPostOnReadonly"))

    def test_get_mail_thread_data_res_users(self):
        """Test flow get thread data for `res.users` record"""
        result = self.res_users_internal_user_email._get_mail_thread_data([])
        self.assertTrue(result.get("hasReadAccess"))
        self.assertFalse(result.get("hasWriteAccess"))

    def test_get_mail_thread_data_empty_user(self):
        """Test flow get thread data for `res.users` empty record"""
        result = self.env["res.users"]._get_mail_thread_data([])
        self.assertFalse(result.get("hasReadAccess"))
        self.assertFalse(result.get("hasWriteAccess"))

    def test_create_conversation_message(self):
        conversation = self.env["cetmix.conversation"].create(
            {"name": "Conversation #1"}
        )
        msg_conversation_1 = self.env["mail.message"].create(
            {
                "author_id": self.res_partner_ann.id,
                "body": "Message #1",
                "partner_ids": [
                    (4, self.env.user.partner_id.id),
                    (4, self.res_partner_kate.id),
                    (4, self.res_partner_mark.id),
                ],
                "res_id": conversation.id,
                "model": conversation._name,
            }
        )
        self.assertEqual(
            conversation.last_message_by.id,
            msg_conversation_1.author_id.id,
            msg=f"Last message author ID must be equal to {self.res_partner_ann.id}",
        )
        msg_conversation_2 = self.env["mail.message"].create(
            {
                "author_id": self.res_partner_kate.id,
                "body": "Message #2",
                "partner_ids": [
                    (4, self.res_partner_kate.id),
                ],
                "res_id": conversation.id,
                "model": conversation._name,
            }
        )
        self.assertEqual(
            conversation.last_message_by.id,
            msg_conversation_2.author_id.id,
            msg=f"Last message author ID must be equal to {self.res_partner_kate.id}",
        )
