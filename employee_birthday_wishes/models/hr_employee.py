from odoo import models,api 
from datetime import datetime

class HrEmployee(models.Model):

    _inherit = "hr.employee"

    def cron_customer_birthday_reminder(self):
        emp_list = self.env['hr.employee'].search([('birthday','!=', False)])
        today = datetime.now().date()
        ctx = self._context.copy()
        email_temp = self.env.ref("employee_birthday_wishes.email_template_birthday")
        for emp in emp_list:
            birthday = emp.birthday 
            if birthday.month == today.month and birthday.day == today.day:
                email_temp.with_context(ctx).send_mail(emp.id)