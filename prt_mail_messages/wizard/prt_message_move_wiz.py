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

from odoo import api, fields, models


#####################
# Mail Move Message #
#####################
class MailMove(models.TransientModel):
    _name = "prt.message.move.wiz"
    _description = "Move Messages To Other Thread"

    model_to = fields.Reference(string="Move to", selection="_referenceable_models")
    lead_delete = fields.Boolean(
        string="Delete Empty Leads",
        help="If all messages are moved from lead and there are no other messages"
        " left except for notifications lead will be deleted",
    )
    opp_delete = fields.Boolean(
        string="Delete Empty Opportunities",
        help="If all messages are moved from opportunity "
        "and there are no other messages"
        " left except for notifications opportunity will be deleted",
    )

    notify = fields.Selection(
        [("0", "Do not notify"), ("1", "Log internal note"), ("2", "Send message")],
        required=True,
        default="0",
        help="Notify followers of destination record",
    )
    is_conversation = fields.Boolean(
        string="Conversation", compute="_compute_is_conversation"
    )
    is_lead = fields.Boolean(string="Lead", compute="_compute_is_lead")

    # -- Any of messages belongs to leads?
    @api.depends_context("active_model", "thread_message_id", "active_ids")
    def _compute_is_lead(self):
        if self._context.get("active_model") != "mail.message":
            self.is_lead = False
            return

        thread_message_id = self._context.get("thread_message_id")
        message_ids = (
            self._context.get("active_ids", [])
            if not thread_message_id
            else [thread_message_id]
        )
        messages = self.env["mail.message"].search(
            [("id", "in", message_ids), ("model", "=", "crm.lead")]
        )
        self.is_lead = len(messages) > 0

    # -- Is Conversation?
    @api.depends_context("active_model")
    def _compute_is_conversation(self):
        self.is_conversation = (
            self._context.get("active_model") == "cetmix.conversation"
        )

    # -- Ref models
    @api.model
    def _referenceable_models(self):
        return self.env["cx.model.reference"].referenceable_models()
