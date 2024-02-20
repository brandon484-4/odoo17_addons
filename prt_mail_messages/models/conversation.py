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

from odoo import _, api, fields, models, tools

from .common import (
    CONVERSATION_TREE_TEMPLATE as TREE_TEMPLATE,
)
from .common import (
    PARTICIPANT_IMG,
    PLAIN_BODY,
)
from .tools import _get_decode_image, _prepare_date_display, sanitize_name


################
# Conversation #
################
class Conversation(models.Model):
    _name = "cetmix.conversation"
    _description = "Conversation"
    _inherit = ["mail.thread"]
    _order = "last_message_post desc, id desc"

    def _default_participants(self):
        """
        User is a participant by default.
        Override in case any custom logic is needed
        """
        return [(4, self.env.user.partner_id.id)]

    active = fields.Boolean(default=True)
    name = fields.Char(string="Subject", required=True, tracking=True)
    author_id = fields.Many2one(
        string="Author",
        comodel_name="res.partner",
        ondelete="set null",
        default=lambda self: self.env.user.partner_id.id,
    )
    partner_ids = fields.Many2many(
        string="Participants", comodel_name="res.partner", default=_default_participants
    )
    last_message_post = fields.Datetime(string="Last Message")
    last_message_by = fields.Many2one(
        string="Last Message", comodel_name="res.partner", ondelete="set null"
    )
    is_participant = fields.Boolean(
        string="I participate", compute="_compute_is_participant"
    )

    subject_display = fields.Html(
        string="Subject", compute="_compute_subject_display", compute_sudo=True
    )
    message_count = fields.Integer(
        string="Messages", compute="_compute_message_count", compute_sudo=True
    )
    message_needaction_count = fields.Integer(
        string="Messages", compute="_compute_message_count", compute_sudo=True
    )

    def name_get(self):
        """Name get. Currently using it only for Move Wizard!"""
        if not self._context.get("message_move_wiz", False):
            return super().name_get()
        return [(rec.id, f"{rec.name} - {rec.author_id.name}") for rec in self]

    @api.depends("message_ids")
    def _compute_message_count(self):
        """
        Compute count messages.
        All messages except for notifications are counted
        """
        for rec in self:
            message_ids = rec.message_ids.filtered(
                lambda msg: msg.message_type != "notification"
            )
            message_needaction = message_ids.filtered(lambda msg: msg.needaction)
            rec.update(
                {
                    "message_count": len(message_ids),
                    "message_needaction_count": len(message_needaction),
                }
            )

    @api.depends("name")
    def _compute_subject_display(self):
        """Get HTML view for Tree View"""
        # Compose subject
        for rec in self.with_context(bin_size=False):
            # Get message date with timezone
            date_display = ""
            message_date = ""
            if rec.last_message_post:
                message_date, date_display = _prepare_date_display(
                    rec, rec.last_message_post
                )
                message_date.replace(tzinfo=None)
            # Compose messages count
            message_count = rec.message_count
            # Total messages
            if message_count == 0:
                message_count_text = _("No messages")
            else:
                msg_text = _("message") if message_count == 1 else _("messages")
                message_count_text = f"{message_count} {msg_text}"
                # New messages
                message_needaction_count = rec.message_needaction_count
                if message_needaction_count > 0:
                    message_count_text = _(
                        "%(msg_count)s, %(need_action_count)s new"
                    ) % {
                        "msg_count": message_count_text,
                        "need_action_count": message_needaction_count,
                    }

            # Participants
            participant_text = " ".join(
                [
                    PARTICIPANT_IMG
                    % {
                        "title": sanitize_name(participant.name),
                        "img": _get_decode_image(participant.image_128),
                    }
                    for participant in rec.partner_ids
                ]
            )
            # Compose preview body
            plain_body = ""
            for message in rec.message_ids:
                if message.message_type != "notification":
                    plain_body = PLAIN_BODY % {
                        "title": sanitize_name(message.author_id.name),
                        "img": _get_decode_image(message.author_avatar),
                        "body": message.preview,
                    }
                    break

            rec.subject_display = TREE_TEMPLATE % {
                "avatar": _get_decode_image(rec.author_id.image_128),
                "title": sanitize_name(rec.author_id.name),
                "author": rec.author_id.name or "",
                "subject": rec.name or "",
                "date": message_date,
                "date_display": date_display,
                "msg_count_text": message_count_text,
                "participant": participant_text,
                "body": plain_body,
            }

    def _compute_is_participant(self):
        """Compute partner is participant"""
        my_id = self.env.user.partner_id.id
        for rec in self:
            rec.is_participant = my_id in rec.partner_ids.ids

    def join(self):
        """Partner joining to conversation"""
        self.ensure_one()
        self.update({"partner_ids": [(4, self.env.user.partner_id.id)]})

    def leave(self):
        """Partner leaving from conversation"""
        self.ensure_one()
        self.sudo().update({"partner_ids": [(3, self.env.user.partner_id.id)]})
        return self.env["ir.actions.act_window"]._for_xml_id(
            "prt_mail_messages.action_conversations"
        )

    # -- Create
    @api.model_create_multi
    def create(self, vals_list):
        # Set current user as author if not defined.
        # Use current date as firs message post
        author_id = self.env.user.partner_id.id
        for vals in filter(lambda val: not val.get("author_id", False), vals_list):
            vals.update({"author_id": author_id})
        res = super(Conversation, self.sudo()).create(vals_list)
        # Subscribe participants
        res.message_subscribe(partner_ids=res.partner_ids.ids)
        return res

    def write(self, vals):
        # Use 'skip_followers_test=True' in context
        # to skip checking for followers/participants
        result = super().write(vals)
        only_conversation = self._context.get("only_conversation", False)
        if "active" in vals.keys() and not only_conversation:
            for rec in self:
                rec.archive_conversion_message(vals.get("active"))

        if self._context.get("skip_followers_test", False):
            # Skip checking for followers/participants
            return result

        # Check if participants changed
        for rec in self:
            msg_partner_ids = rec.message_partner_ids.ids
            partner_ids = rec.partner_ids.ids
            # New followers added?
            followers_add = list(
                filter(lambda p: p not in msg_partner_ids, partner_ids)
            )
            if followers_add:
                rec.message_subscribe(partner_ids=followers_add)

            # Existing followers removed?
            followers_remove = list(
                filter(lambda p: p not in partner_ids, msg_partner_ids)
            )
            if followers_remove:
                rec.message_unsubscribe(partner_ids=followers_remove)

        return result

    def archive_conversion_message(self, active_state):
        """Set archive state for related mail messages"""
        messages = self.env["mail.message"].search(
            [
                ("active", "=", not active_state),
                ("model", "=", self._name),
                ("res_id", "=", self.id),
                ("message_type", "!=", "notification"),
            ]
        )
        msg_vals = {"active": active_state}
        if active_state:
            msg_vals.update(delete_uid=False, delete_date=False)
        messages.write(msg_vals)

    # -- Search for partners by email.
    @api.model
    def partner_by_email(self, email_addresses):
        """
        Override this method to implement custom search
         (e.g. if using prt_phone_numbers module)
        :param list email_addresses: List of email addresses
        :return: res.partner obj if found.
        Please pay attention to the fact that only
         the first (newest) partner found is returned!
        """
        # Use loop with '=ilike' to resolve MyEmail@GMail.com cases
        res_partner_obj = self.env["res.partner"]
        for address in email_addresses:
            partner = res_partner_obj.search(
                [("email", "=ilike", address)], limit=1, order="id desc"
            )
            if partner:
                return partner

    @api.model
    def get_or_create_partner_id_by_email(self, email):
        """
        Get or create partner id
        :param str email: email address
        :rtype: int
        :return: partner id
        """
        if not email:
            return False
        res_partner_obj = self.env["res.partner"]
        parsed_name, parsed_email = res_partner_obj._parse_partner_name(email)
        partner = self.partner_by_email([parsed_email])
        if partner:
            return partner.id
        category = self.env.ref(
            "prt_mail_messages.cetmix_conversations_partner_cat",
            raise_if_not_found=False,
        )
        create_values = {
            "name": parsed_name or parsed_email,
            "category_id": [(4, category.id)] if category else False,
        }
        if parsed_email:
            create_values["email"] = parsed_email
        return res_partner_obj.create(create_values).id

    @api.model
    def prepare_partner_ids(self, email_list):
        """
        Prepare set of partner ids
        :param list email_list: list of email addresses
        :rtype: set
        :return: set of partner ids
        """
        if not email_list:
            return set()
        return {
            self.get_or_create_partner_id_by_email(email)
            for email in tools.email_split_and_format(email_list)
        }

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        """Parse incoming email"""
        custom_values = custom_values or {}
        partner_ids = set()

        # 1. Check for author. If does not exist create new partner.
        author_id = msg_dict.get("author_id")
        email_from = msg_dict.get("email_from")
        if not author_id and email_from:
            author_id = self.get_or_create_partner_id_by_email(email_from)
            # Update message author
            msg_dict.update({"author_id": author_id})

        # Append author to participants (partners)
        partner_ids.add(author_id)

        # To
        partner_ids |= self.prepare_partner_ids(msg_dict.get("to"))
        # Cc
        partner_ids |= self.prepare_partner_ids(msg_dict.get("cc"))

        # Update custom values
        custom_values.update(
            {
                "name": msg_dict.get("subject", "").strip(),
                "author_id": author_id,
                "partner_ids": [(4, pid) for pid in partner_ids if pid],
            }
        )
        return super(
            Conversation, self.with_context(mail_create_nolog=True)
        ).message_new(msg_dict, custom_values)
