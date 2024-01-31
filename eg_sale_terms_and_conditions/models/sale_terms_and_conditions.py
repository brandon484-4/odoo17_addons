from odoo import fields, models


class SaleTermsAndConditions(models.Model):
    _name = 'sale.terms.and.conditions'
    _description = 'sale terms and conditions'
    _rec_name = 'terms'

    terms = fields.Char(string='Terms')
    condition = fields.Html(string='Terms & Conditions')
