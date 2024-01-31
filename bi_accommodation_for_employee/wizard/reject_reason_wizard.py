# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class RejectReason(models.TransientModel):
    _name = 'reject.reason.wizard'
    _description = ' Reject Reason'

    reason_reject = fields.Char(string='Reject Reason',required=True)

    def update_dates(self):
        value = self.env['employee.accommodation'].browse(self.env.context.get('active_id'))
        value.update({'reject_reason': self.reason_reject,
                       'state':'reject'})
        return value