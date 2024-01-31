from dateutil.relativedelta import relativedelta
from odoo import api, models, fields, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.model
    def _cron_employee_contract_reminder(self):
        """
        Cron job to send email to employee
        :return:
        """
        contract_ids = self.get_contracts_to_remind().filtered(lambda contract: contract.employee_id.work_email)
        contract_ids.send_mail_reminder()
        return contract_ids

    @api.model
    def get_contracts_to_remind(self):
        """
        Get contracts to remind
        :return:
        """
        contract_reminder_days = self.env['ir.config_parameter'].sudo().get_param('employee_contract_reminder.contract_reminder_days')
        if not contract_reminder_days:
            return []
        contract_ids = self.search([
            ('state', '=', 'open'),
            ('date_end', '!=', False),
            ('date_end', '>=', fields.Date.today()),
            ('date_end', '<=', fields.Date.today() + relativedelta(days=int(contract_reminder_days)))
        ])
        return contract_ids

    def send_mail_reminder(self):
        """
        Send email to employee
        :return:
        """
        template = self.env.ref('employee_contract_reminder.email_template_employee_contract_reminder')
        for contract in self:
            template.send_mail(contract.id, force_send=True, email_values={'email_to': contract.employee_id.work_email})
