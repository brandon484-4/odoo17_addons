# -*- coding: utf-8 -*-
{
    "name": "Send Message Composer",
    "version": "17.0.1.0.1",
    "category": "Discuss",
    "author": "faOtools",
    "website": "https://faotools.com/apps/17.0/send-message-composer-856",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "mail"
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/data.xml"
    ],
    "assets": {
        "web.assets_backend": [
                "mail_composer_on_send_message/static/src/core/web/chatter.js",
                "mail_composer_on_send_message/static/src/core/common/composer.js"
        ]
},
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to always open a full composer on the button 'Send Message'",
    "description": """For the full details look at static/description/index.html
* Features *""",
    "images": [
        "static/description/main.png"
    ],
    "price": "0.0",
    "currency": "EUR",
}