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

from odoo.tests import Form

from .common import MailMessageCommon


class TestMessageEdit(MailMessageCommon):
    """
    TEST 1 : Check correct message move functions
    """

    # -- TEST 1 : Check correct message move functions
    def test_message_move(self):
        """Check correct message move functions"""
        MessageMove = self.env["prt.message.move.wiz"]
        with Form(MessageMove.with_context(active_model="crm.lead")) as form:
            self.assertFalse(form.is_lead)
            self.assertFalse(form.is_conversation)
        with Form(
            MessageMove.with_context(
                thread_message_id=self.mail_message_test_conversation.id
            )
        ) as form:
            self.assertFalse(form.is_lead)
            self.assertFalse(form.is_conversation)
        with Form(MessageMove.with_context(active_model="cetmix.conversation")) as form:
            self.assertFalse(form.is_lead)
            wiz = form.save()
            self.assertTrue(wiz.is_conversation)
