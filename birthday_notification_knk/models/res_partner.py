# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>)

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    birthday = fields.Date(string='Birthday')

    @api.model
    def send_birthday_notification(self):
        today = fields.Date.context_today(self)
        for partner in self.env['res.partner'].search([('birthday', '!=', False), ('email', '!=', False)]):
            if partner.company_id.send_contact_birthday_notification or self.env.company.send_contact_birthday_notification:
                if today == partner.birthday:
                    template_id = self.env.ref('birthday_notification_knk.contact_birthday_notification_template')
                    template_id.send_mail(partner.id, force_send=True)

