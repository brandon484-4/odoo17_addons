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

from datetime import datetime

from odoo import _
from odoo.fields import Datetime

from .common import IMAGE_PLACEHOLDER, MONTHS


def _get_decode_image(image):
    """Decode image to 'utf-8' or return default image"""
    if image:
        return image.decode("utf-8")
    return IMAGE_PLACEHOLDER


def sanitize_name(name):
    """In case name contains @. Use to keep html working"""
    if not name:
        return ""
    return name.split("@")[0] if "@" in name else name


def _prepare_date_display(record, date):
    """Compose displayed date/time"""
    now = Datetime.context_timestamp(record, Datetime.now())
    message_date = Datetime.context_timestamp(record, date)
    days_diff = (now.date() - message_date.date()).days
    date_format = datetime.strftime(message_date, "%H:%M")
    if days_diff == 0:
        date_display = date_format
    elif days_diff == 1:
        date_display = _("Yesterday %s", date_format)
    elif now.year == message_date.year:
        date_display = _("%(day)s %(month)s") % {
            "day": message_date.day,
            "month": MONTHS.get(message_date.month),
        }
    else:
        date_display = str(message_date.date())
    return message_date, date_display


def _prepare_notification(
    title,
    needaction=None,
    starred=None,
    has_error=None,
    cx_edit_uid=None,
    attachment_ids=None,
    icons=None,
):
    """Prepare notification string"""
    notification_icons = icons or ""
    if needaction:
        notification_icons = '<i class="fa fa-envelope" title="%s"></i>' % title
    if starred:
        notification_icons = ' &nbsp;<i class="fa fa-star" title="%s"></i>' % title
    if has_error:
        notification_icons = (
            ' &nbsp;<i class="fa fa-exclamation" title="%s"></i>' % title
        )
    # .. edited
    if cx_edit_uid:
        notification_icons = (
            ' &nbsp;<i class="fa fa-edit"'
            ' style="color:#1D8348;"'
            ' title="%s"></i>' % title
        )
    # .. attachments
    if attachment_ids:
        notification_icons = ' &nbsp;<i class="fa fa-paperclip" title="%s"></i>' % title
    return notification_icons
