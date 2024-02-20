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

{
    "name": "Mail Messages Easy",
    "version": "17.0.1.0.12",
    "summary": """
Read and manage all Odoo messages in one place!
Show all messages, Show sent message, Reply to messages,
Forward messages, Edit messages, Delete messages, Move messages, Quote messages
""",
    "author": "Ivan Sokolov, Cetmix",
    "category": "Discuss",
    "license": "LGPL-3",
    "website": "https://cetmix.com",
    "depends": ["mail"],
    "live_test_url": "https://demo.cetmix.com",
    "images": ["static/description/banner.gif"],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/rules.xml",
        "data/data.xml",
        "data/ir_cron_data.xml",
        "views/actions.xml",
        "views/mail_message_views.xml",
        "views/cetmix_conversation_views.xml",
        "views/res_partner_views.xml",
        "views/cx_model_reference_views.xml",
        "views/res_config_settings_views.xml",
        "report/mail_message_paperformat.xml",
        "report/mail_message_report.xml",
        "wizard/message_edit.xml",
        "wizard/message_partner_assign.xml",
        "wizard/message_move.xml",
        "wizard/mail_compose_message.xml",
    ],
    "demo": ["demo/demo.xml"],
    "assets": {
        "web.assets_backend": [
            "prt_mail_messages/static/src/views/list/*",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
