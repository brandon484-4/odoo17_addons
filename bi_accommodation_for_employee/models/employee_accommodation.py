# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import json as simplejson
# import simplejson
from lxml import etree

from odoo import models, fields, api
from odoo.exceptions import UserError

class EmployeeAccomomdation:
    pass


class EmployeeAccommomdation(models.Model):
    _name = 'employee.accommodation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'request_seq'
    _description = 'Employee Accommodation'

    request_seq = fields.Char("Request Code", copy=False, readonly=True, default=lambda self: ('New'), tracking=True)
    name = fields.Char(string='Name',tracking=True)
    employee_id = fields.Many2one('hr.employee',string="Employee Name", required=True,tracking=True)
    expense_id = fields.Many2one('hr.expense',string="Employee Expenses",tracking=True,copy=False)
    email = fields.Char(string='Employee Email',tracking=True)
    phone = fields.Char(string='Employee Phone',tracking=True)
    amount = fields.Float('Total Expenses',readonly=True,compute='_compute_total_expense')
    manager_id = fields.Many2one('hr.employee', string="Employee Manager",required=True,tracking=True)
    department_id = fields.Many2one("hr.department", string="Employee Departments")
    req_date = fields.Date(string="Request Date",required=True)
    location_id = fields.Many2one('bi.location', string="Enter Trip Location Name", required=True)
    company_id = fields.Many2one('res.company',string='Company',copy=False)
    reject_reason = fields.Char('Reject Reason')
    description = fields.Html('Description')
    paid_by = fields.Selection([
        ('company_account', 'Company'),
        ('own_account', 'Employee'),
    ], string='Paid By', default='company_account', required=True,tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('manager', 'Submitted To Manager'),
        ('hr', 'Submitted To HR'),
        ('expenses', 'Expenses Generated'),
        ('reject', 'Rejected'),
    ], string='Status', default='draft', tracking=True)
    book_ids = fields.One2many(
        'employee.accommodation.hotel.book', 'accommodation_id', string='Hotels', help="Book Hotel")

    @api.model
    def create(self, vals):
        vals['request_seq'] = self.env['ir.sequence'].next_by_code('employee.accommodation') or 'New'
        rec = super(EmployeeAccommomdation, self).create(vals)
        return rec

    def write(self, vals):
        if not self.request_seq or self.request_seq == 'New':
            vals['request_seq'] = self.env['ir.sequence'].next_by_code('employee.accommodation')
        return super(EmployeeAccommomdation, self).write(vals)

    @api.onchange('employee_id')
    def _onchange_employee(self):
        if self.employee_id:
            self.email = self.employee_id.work_email
            self.phone = self.employee_id.work_phone
            self.manager_id = self.employee_id.parent_id.id
            self.department_id = self.employee_id.department_id.id
            self.company_id = self.employee_id.company_id.id

    def send_manager(self):
        self.state = 'manager'
        if not self.book_ids:
            raise UserError(' Please Fill Hotel Related Details. ')

    def send_hr(self):
        if self.amount == 0:
            raise UserError(' Please approve at least one hotel related booking otherwise status of application move to reject.')
        self.state = 'hr'

    def expense_total(self):
        product_id = self.env['product.product'].sudo().search([('name','=','Accommodation')])
        if not product_id:
            create_product = self.env['product.product'].sudo().create({'name':'Accommodation'})
            vals = {
                'name': 'Tour Of '+ self.location_id.location_name,
                'product_id':create_product.id,
                'total_amount':self.amount,
                'payment_mode':self.paid_by,
                'employee_id':self.employee_id.id,
                'date':self.req_date,
                'quantity':1,
                'company_id':self.company_id.id,
            }
            create_expense = self.env['hr.expense'].sudo().create(vals)
            self.expense_id = create_expense.id
            self.state = 'expenses'
        else:
            vals = {
                'name': 'Tour Of '+ self.location_id.location_name,
                'product_id': product_id.id,
                'total_amount': self.amount,
                'payment_mode': self.paid_by,
                'employee_id': self.employee_id.id,
                'date': self.req_date,
                'quantity': 1,
                'company_id': self.company_id.id,
            }
            create_expense = self.env['hr.expense'].sudo().create(vals)
            self.expense_id = create_expense.id
            self.state = 'expenses'

    def reject_request(self):
        return {
            'name': 'Reject Reason ',
            'view_mode': 'form',
            'res_model': 'reject.reason.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def view_expenses(self):
        if self.expense_id:
            return {
                'name': 'Employee Accommodation',
                'view_mode': 'form',
                'res_model': 'hr.expense',
                'type': 'ir.actions.act_window',
                'res_id': self.expense_id.id,
                'view_type': 'form',
                'target': 'current',
            }
        else:
            pass
    @api.depends('book_ids')
    def _compute_total_expense(self):
        total = 0
        for rec in self.book_ids:
            if rec.state == 'approve':
                total += rec.total_cost
            if rec.state == 'draft' and self.state == 'hr':
                rec.state = 'reject'
        if total:
            self.amount = total
        else:
            self.amount = 0.0

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        result = super(EmployeeAccommomdation, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                                    toolbar=toolbar,
                                                                    submenu=submenu)
        doc = etree.XML(result['arch'])
        if view_type == 'form':
            for node in doc.xpath("//field"):
                modifiers = simplejson.loads(node.get("modifiers"))
                if 'readonly' not in modifiers:
                    modifiers['readonly'] = [['state', 'not in', ['draft']]]
                else:
                    if type(modifiers['readonly']) != bool:
                        modifiers['readonly'].insert(0, '|')
                        modifiers['readonly'] += [['state', 'not in', ['draft']]]
                node.set('modifiers', simplejson.dumps(modifiers))
                result['arch'] = etree.tostring(doc)

        return result


class EmployeeAccommomdationHotel(models.Model):
    _name = 'employee.accommodation.hotel.book'
    _description = 'Employee Accommodation Hotel Book'

    hotel_id = fields.Many2one('bi.hotel', string="Hotel Name",domain="[('location_id', '=', location_id)]",required=True)
    starting_date = fields.Date(string="Start Date", copy=False)
    ending_date = fields.Date(string="End Date", copy=False)
    count_day = fields.Integer(string="No. of Days", copy=False,compute='_compute_days',default=1)
    cost_per_day = fields.Float(string="Cost Per Day", copy=False)
    total_cost = fields.Float(string="Total Cost", compute='_compute_total_cost', copy=False)
    location_id = fields.Many2one('bi.location', string="Trip Location Name",related='accommodation_id.location_id',required=True)
    accommodation_id = fields.Many2one('employee.accommodation', string="Accommodation")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approve', 'Approve'),
        ('reject','Reject')
    ], string='Status', default='draft', tracking=True)

    @api.depends('starting_date','ending_date')
    def _compute_days(self):
        for rec in self:
            if rec.starting_date and rec.ending_date:
                valid = int((rec.starting_date - rec.ending_date).days)
                if valid > 0:
                    raise UserError('Oops! You Select End Date Before Start Date Please Check. ')
                if rec.starting_date == rec.ending_date:
                    rec.count_day = 1
                else:
                    rec.count_day = abs(int((rec.starting_date - rec.ending_date).days)) + 1
            else:
                rec.count_day = 1

    @api.depends('cost_per_day')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = (rec.cost_per_day * rec.count_day)

    def book_approve(self):
        if self.state == 'draft':
            self.state = 'approve'

    def book_reject(self):
        if self.state == 'draft':
            self.state = 'reject'

