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

from odoo import fields
from odoo.tests import common


@common.tagged("post_install", "-at_install", "test_conversation")
class TestMailMessageConversation(common.TransactionCase):
    """
    TEST 1 : Unlink all messages from conversation
        [Get conversation messages]
        - count messages is 2
        [Messages move to trash (unlink_pro)]
        - conversation active is False
        - conversation message #1 active is False
        - conversation message #1 delete uid is not empty
        - conversation message #1 delete date is not empty
        - conversation message #2 active is False
        - conversation message #2 delete uid is not empty
        - conversation message #2 delete date is not empty
        [Get conversation messages]
        [Message delete (unlink_pro)]
        - message #1 not found
        - message #2 not found

    TEST 2 : Get (undelete) message from trash
        [Get conversation messages]
        [messages moveto trash]
        - conversation # 1 active is False
        - conversation message #1 active is False
        - conversation message #1 delete uid is not empty
        - conversation message #1 delete date is not empty
        - conversation message #2 active is False
        - conversation message #2 delete uid is not empty
        - conversation message #2 delete date is not empty
        [Message undelete]
        - conversation #1 active is True
        - conversation message #1 active is True
        - conversation message #2 active is True

    TEST 3 : Delete message by cron
        [Set config delete trash days = 1]
        [compute date on three days ago]
        [Create mail message]
        [Start cron unlink function (_unlink_trash_message)]
        [Get message by field 'reply to']
        - message is not found

    TEST 4 : Unlink empty conversation
        [Set config delete trash days = 1]
        [Move to trash conversation message #1 and #2]
        [Unlink messages by cron from trash]
        - conversation not found

    TEST 5 : Get or create new partner by Email
        [Get or create partner id by email 'Test Partner <test.partner@example.com>']
        - partner id must be equal res_partner_test_1.id
        [Get partner by email 'partner.example@example.com']
        - partners recordset must be empty
        [Get or create partner id by email
        'Partner Example <partner.example@example.com>']
        [Get partner by email 'partner.example@example.com']
        - partner id must be equal to 'Partner Example' id

    TEST 6 : Get conversations name get
        - result must be equal to [(conversation.id, "Test Conversation #1")]
        - result must be equal to
        [(conversation.id,  "Test Conversation #1 - env.user.name")]

    TEST 7 : Test conversation messages count
        [Create 'Test Conversation Test #1' conversation]
        - conversation message_ids count must be equal to 1
        - conversation message_count must be equal to 0
        [Create Mail Message]
        - conversation message_ids count must be equal to 2
        - conversation message_count must be equal to 1
        [Create Internal Message]
        - conversation message_ids count must be equal to 3
        - Conversation message_count must be equal to 1

    TEST 8 : User is participant in conversation
        - demo user is participant in cetmix_conversation_1 conversation
        [Delete demo user from cetmix_conversation_1 conversation]
        - user is not access to cetmix_conversation_1 record

    TEST - 9 : Get the first partner found
        [Get partner by empty email list]
        - result is None
        [Get partner by undefined email in list]
        - result is None
        [Create Partner by email 'partner.example@example.com']
        [Get partner by list :
        ["test.partner@example.com", "partner.example@example.com"]]
        - result: Partner must be equal to Partner 'test.partner@example.com'
    """

    def setUp(self):
        super().setUp()
        self.res_users_demo = self.env.ref("base.user_demo", raise_if_not_found=False)
        self.res_user_system = self.env.ref("base.user_admin", raise_if_not_found=False)
        self.res_partner_test_1 = self.env.ref(
            "prt_mail_messages.res_partner_test_1", raise_if_not_found=False
        )
        self.cetmix_conversation_1 = self.env.ref(
            "prt_mail_messages.cetmix_conversation_test_1", raise_if_not_found=False
        )
        self.cetmix_conversation_2 = self.env.ref(
            "prt_mail_messages.cetmix_conversation_test_2", raise_if_not_found=False
        )
        self.mail_message_1 = self.env.ref(
            "prt_mail_messages.mail_message_test_1", raise_if_not_found=False
        )
        self.mail_message_2 = self.env.ref(
            "prt_mail_messages.mail_message_test_2", raise_if_not_found=False
        )

    def _get_messages_by_conversation_id(self, conversation_id):
        return (
            self.env["mail.message"]
            .with_context(active_test=False)
            .search(
                [
                    ("res_id", "=", conversation_id),
                    ("message_type", "!=", "notification"),
                ]
            )
        )

    # -- TEST 1 : Unlink all messages from conversation
    def test_unlink_conversation_message(self):
        """Unlink all messages from conversation"""

        # Get conversation messages
        # Messages count: 2
        # Messages move to trash
        # Conversation active: False
        # Message #1 active: False
        # Message #1 Delete UID: False
        # Message #1 Delete Date: False
        # Message #2 active: False
        # Message #2 Delete UID: False
        # Message #2 Delete Date: False
        # Get conversation messages
        # Conversation messages delete
        # Messages #1 count: 0
        # Messages #2 count: 0
        messages = self._get_messages_by_conversation_id(self.cetmix_conversation_1.id)
        messages.unlink_pro()

        self.assertFalse(self.cetmix_conversation_1.active, msg="Active must be False")
        self.assertFalse(self.mail_message_1.active, msg="Active must be False")
        self.assertNotEqual(
            self.mail_message_1.delete_uid, False, msg="Delete UID must not be set"
        )
        self.assertNotEqual(
            self.mail_message_1.delete_date, False, msg="Delete Date must not be set"
        )
        self.assertFalse(self.mail_message_2.active, "Active must be False")
        self.assertNotEqual(
            self.mail_message_2.delete_uid, False, msg="Delete UID must not be set"
        )
        self.assertNotEqual(
            self.mail_message_2.delete_date, False, msg="Delete Date must not be set"
        )
        messages = self._get_messages_by_conversation_id(self.cetmix_conversation_1.id)
        messages.unlink_pro()
        mail_message_1_ids = self.env["mail.message"].search(
            [("id", "=", self.mail_message_1.id)]
        )
        self.assertFalse(mail_message_1_ids, msg="Recordset must be empty")
        mail_message_2_ids = self.env["mail.message"].search(
            [("id", "=", self.mail_message_2.id)]
        )
        self.assertFalse(mail_message_2_ids, msg="Recordset must be empty")

    # -- TEST 2 : Get (undelete) message from trash
    def test_undelete_conversation(self):
        """Get (undelete) message from trash"""

        # Get conversation messages
        # Messages move to trash
        # Conversation active: False
        # Message #1 active: False
        # Message #1 Delete UID: user.id
        # Message #1 Delete Date: date
        # Message #2 active: False
        # Message #2 Delete UID: user.id
        # Message #2 Delete Date: date
        # Conversation messages delete
        # Conversation active: True
        # Message #1 active: True
        # Message #2 active: True
        messages = self._get_messages_by_conversation_id(self.cetmix_conversation_1.id)
        messages.unlink_pro()
        self.assertFalse(self.cetmix_conversation_1.active, msg="Active must be False")
        self.assertFalse(self.mail_message_1.active, msg="Active must be False")
        self.assertNotEqual(
            self.mail_message_1.delete_uid,
            False,
            msg="Messages #1 Delete UID must be set",
        )
        self.assertNotEqual(
            self.mail_message_1.delete_date,
            False,
            msg="Message #1 Delete Date must be set",
        )
        self.assertFalse(self.mail_message_2.active, msg="Active must be False")
        self.assertNotEqual(
            self.mail_message_2.delete_uid,
            False,
            msg="Messages #2 Delete UID must be set",
        )
        self.assertNotEqual(
            self.mail_message_2.delete_date,
            False,
            msg="Message #2 Delete Date must be set",
        )
        messages.undelete()
        self.assertTrue(self.cetmix_conversation_1.active, msg="Active must be True")
        self.assertTrue(self.mail_message_1.active, msg="Active must be True")
        self.assertTrue(self.mail_message_2.active, msg="Active must be True")

    # -- TEST 3 : Delete message by cron
    def test_unlink_trash_message(self):
        """Delete message by cron"""

        # Set config delete trash days: 1
        # Compute date on three days ago
        # Create mail message
        # Start cron unlink function (_unlink_trash_message)
        # Get message by field 'reply to'
        # Messages count: 0
        self.env["ir.config_parameter"].sudo().set_param(
            "cetmix.messages_easy_empty_trash", 1
        )
        self.env["mail.message"]._unlink_trash_message()
        mail_message = (
            self.env["mail.message"]
            .sudo()
            .search([("reply_to", "=", "test.expl@example.com")])
        )
        self.assertEqual(len(mail_message), 0, msg="Messages count must be equal to 0")

    # -- TEST 4 : Unlink empty conversation
    def test_unlink_all_conversation_message(self):
        """Unlink empty conversation"""

        # Set config delete trash days: 1
        # Move to trash conversation message: #1 and #2
        # Unlink messages by cron from trash
        # Conversations count: 0
        self.env["ir.config_parameter"].sudo().set_param(
            "cetmix.messages_easy_empty_trash", 1
        )
        self.cetmix_conversation_1.message_ids.unlink_pro()
        self.env["mail.message"]._unlink_trash_message(
            test_custom_datetime=fields.Datetime.now()
        )
        empty_conversation_1 = (
            self.env["cetmix.conversation"]
            .with_context(active_test=False)
            .search(
                [
                    ("id", "=", self.cetmix_conversation_1.id),
                ]
            )
        )
        self.assertFalse(
            empty_conversation_1, msg="Conversations recordset must be empty"
        )

    # TEST - 5 : Get or create new partner by Email
    def test_get_or_create_partner(self):
        """Get or create new partner by Email"""

        # Get or create partner id by email 'Test Partner <test.partner@example.com>'
        # Partner id: res_partner_test_1.id
        # Get partner by email 'partner.example@example.com'
        # Partners recordset: empty
        # Get or create partner id by email
        # 'Partner Example <partner.example@example.com>'
        # Get partner by email 'partner.example@example.com'
        # Partner id: 'Partner Example' id
        CetmixConversation = self.env["cetmix.conversation"]
        email = "Test Partner <test.partner@example.com>"
        partner_id = CetmixConversation.get_or_create_partner_id_by_email(email)
        self.assertEqual(
            self.res_partner_test_1.id,
            partner_id,
            msg=f"Partner id must be equal to {partner_id}",
        )
        empty_partner = self.env["res.partner"].search(
            [("email", "=ilike", "partner.example@example.com")], limit=1
        )
        self.assertFalse(empty_partner, msg="Recordset must be empty")
        created_partner_id = CetmixConversation.get_or_create_partner_id_by_email(
            "Partner Example <partner.example@example.com>"
        )
        partner_id = (
            self.env["res.partner"]
            .search([("email", "=ilike", "partner.example@example.com")], limit=1)
            .id
        )
        self.assertEqual(
            partner_id,
            created_partner_id,
            msg=f"Partner id must be equal to {created_partner_id}",
        )

    # TEST - 6 : Get conversations name get
    def test_conversations_name_get(self):
        """Get conversations name get"""

        # Default name_get: [(conversation.id, "Test Conversation #1")]
        # name_get with context 'message_move_wiz':
        # [(conversation.id,  "Test Conversation #1 - env.user.name")]
        expected_result = [(self.cetmix_conversation_1.id, "Test Conversation #1")]
        result = self.cetmix_conversation_1.name_get()
        self.assertEqual(result, expected_result, msg="Lists must be the same")
        result = self.cetmix_conversation_1.with_context(message_move_wiz=1).name_get()
        expected_result = [
            (
                self.cetmix_conversation_1.id,
                f"Test Conversation #1 - {self.env.user.name}",
            )
        ]
        self.assertEqual(result, expected_result, msg="Lists must be the same")

    # TEST - 7 : Test conversation messages count
    def test_conversation_messages_count(self):
        """ "Test conversation messages count"""

        # Create 'Test Conversation Test #1' conversation
        # Conversation message_ids count: 1
        # Conversation message_count: 0
        # Create Mail Message
        # Conversation message_ids count: 2
        # Conversation message_count: 1
        # Create Internal Message
        # Conversation message_ids count: 3
        # Conversation message_count: 1
        self.assertEqual(
            len(self.cetmix_conversation_2.message_ids),
            1,
            msg="Messages IDS count must be equal to 1",
        )
        self.assertEqual(
            self.cetmix_conversation_2.message_count,
            0,
            msg="Messages count must be equal to 0",
        )

        self.env["mail.message"].create(
            {
                "res_id": self.cetmix_conversation_2.id,
                "model": "cetmix.conversation",
                "reply_to": "test.reply@example.com",
                "email_from": "test.from@example.com",
                "body": "Mail message Body #1",
            }
        )

        self.assertEqual(
            len(self.cetmix_conversation_2.message_ids),
            2,
            msg="Messages IDS count must be equal to 2",
        )
        self.assertEqual(
            self.cetmix_conversation_2.message_count,
            1,
            msg="Messages count must be equal to 1",
        )
        self.cetmix_conversation_2.message_post(body="Test Message")
        self.assertEqual(
            len(self.cetmix_conversation_2.message_ids),
            3,
            msg="Messages IDS count must be equal to 3",
        )
        self.assertEqual(
            self.cetmix_conversation_2.message_count,
            1,
            msg="Messages count must be equal to 1",
        )

    # TEST - 8 : User is participant in conversation
    def test_user_is_participant(self):
        """User is participant in conversation"""

        # Demo user is participant in cetmix_conversation_1 conversation
        # Delete demo user from cetmix_conversation_1 conversation
        # Demo user is not access to cetmix_conversation_1 record

        is_participant = self.cetmix_conversation_1.with_user(
            self.res_users_demo.id
        ).is_participant
        self.assertTrue(
            is_participant,
            msg=f"Demo User is participant in #{self.cetmix_conversation_1.id} conversation.",  # noqa
        )
        self.cetmix_conversation_1.with_user(self.res_users_demo.id).leave()
        record = (
            self.env["cetmix.conversation"]
            .with_user(self.res_users_demo.id)
            .search([("id", "=", self.cetmix_conversation_1.id)])
        )
        self.assertFalse(record, msg="Recordset must be emapty")

    # TEST - 9 : Get the first partner found
    def test_get_first_found_partner_by_email(self):
        """Get the first partner found"""

        # Get partner by empty email list
        # Result: None
        # Get partner by undefined email in list
        # Result: None
        # Create Partner by email 'partner.example@example.com'
        # Get partner by list :
        # ["test.partner@example.com", "partner.example@example.com"]
        # Result: Partner with email 'test.partner@example.com'
        Conversation = self.env["cetmix.conversation"]

        result = Conversation.partner_by_email([])
        self.assertIsNone(result, msg="Result must be None")
        emails = ["partner.example@example.com"]
        result = Conversation.partner_by_email(emails)
        self.assertIsNone(result, msg="Result must be None")

        Conversation.get_or_create_partner_id_by_email(
            "Partner Example <partner.example@example.com>"
        )
        emails = ["test.partner@example.com", "partner.example@example.com"]
        result = Conversation.partner_by_email(emails)
        self.assertEqual(
            result.id,
            self.res_partner_test_1.id,
            msg=f"Result must be equal to ID #{result.id} Partner",
        )

    def test_cetmix_conversation_create(self):
        """Test flow when author is not defined on create"""
        Conversation = self.env["cetmix.conversation"]
        vals_without_author = {
            "active": True,
            "name": "Test Conversation #1",
            "partner_ids": [(4, self.res_partner_test_1.id)],
        }
        conversation = Conversation.create(vals_without_author)
        self.assertEqual(
            conversation.author_id.id,
            self.env.user.partner_id.id,
            msg=f"Conversation Author ID must be equal to {self.env.user.partner_id.id}",  # noqa
        )
        # Author is defined on create
        vals_with_author = vals_without_author.copy()
        vals_with_author.update(author_id=self.res_partner_test_1.id)
        conversation = Conversation.create(vals_with_author)
        self.assertEqual(
            conversation.author_id.id,
            self.res_partner_test_1.id,
            msg=f"Conversation Author ID must be equal to {self.res_partner_test_1.id}",
        )
