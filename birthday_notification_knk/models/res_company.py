# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>)

from odoo import models, fields


class res_company(models.Model):
    _inherit = 'res.company'

    send_contact_birthday_notification = fields.Boolean()
    send_employee_birthday_notification = fields.Boolean()
