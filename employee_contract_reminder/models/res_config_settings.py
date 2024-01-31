# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    contract_reminder_days = fields.Integer(string='Contract Reminder Days',
                                            config_parameter='employee_contract_reminder.contract_reminder_days')
