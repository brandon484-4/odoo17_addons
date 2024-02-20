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

from markupsafe import Markup

from odoo.tests import Form

from .common import MailMessageCommon


class TestMessageEdit(MailMessageCommon):
    """
    TEST 1 : Check access to edit message
    TEST 2 : Check correct default value for the message editing
    """

    # -- TEST 1 : Check access to edit message
    def test_edit_message_access(self):
        """Check access to edit message"""
        EditWiz = self.env["cx.message.edit.wiz"]
        edit_wiz = EditWiz.with_context(active_ids=self.mail_message_test_1.ids).new()
        self.mail_message_test_1.author_id = False
        self.assertFalse(edit_wiz.can_edit)
        edit_wiz = (
            EditWiz.sudo().with_context(active_ids=self.mail_message_test_1.ids).new()
        )
        self.mail_message_test_1.author_id = self.res_partner_ann.id
        self.assertTrue(edit_wiz.can_edit)
        edit_wiz = (
            EditWiz.with_user(self.test_user)
            .with_context(active_ids=self.mail_message_test_conversation.ids)
            .new()
        )
        self.assertFalse(edit_wiz.can_edit)
        self.test_user.write(
            {
                "groups_id": [
                    (4, self.ref("prt_mail_messages.group_conversation_all")),
                    (4, self.ref("prt_mail_messages.group_messages_edit_all")),
                ]
            }
        )
        self.mail_message_test_conversation.write(
            {"subtype_id": self.env.ref("mail.mt_comment").id}
        )
        edit_wiz = (
            EditWiz.with_user(self.test_user)
            .with_context(active_ids=self.mail_message_test_conversation.ids)
            .new()
        )
        self.assertTrue(edit_wiz.can_edit)

    # -- TEST 2 : Check correct default value for the message editing
    def test_default_edit_message(self):
        """Check correct default value for the message editing"""
        EditWiz = self.env["cx.message.edit.wiz"]

        with Form(
            EditWiz.with_context(active_ids=self.mail_message_test_1.ids)
        ) as form:
            self.assertEqual(
                form.message_id,
                self.mail_message_test_1,
                msg=f"Message must be equal to record with ID {self.mail_message_test_1.id}",  # noqa
            )
            self.assertEqual(form.body, Markup("<p>Test Body Child</p>"))
            self.assertTrue(form.can_edit, msg="Can_edit must be True")
        with Form(
            EditWiz.with_context(active_ids=self.mail_message_parent.ids)
        ) as form:
            self.assertEqual(
                form.message_id,
                self.mail_message_parent,
                msg=f"Message must be equal to record with ID {self.mail_message_parent.id}",  # noqa
            )
            self.assertEqual(form.body, Markup("<p>Test Body Parent</p>"))
            self.assertTrue(form.can_edit, msg="Can_edit must be True")
        with Form(EditWiz) as form:
            self.assertFalse(form.message_id, msg="Message must be empty")
            self.assertFalse(form.can_edit, msg="Can_edit must be False")
            self.assertFalse(form.body, msg="Can_edit must be False")
