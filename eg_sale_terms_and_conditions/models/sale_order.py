from odoo import fields, api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    terms_id = fields.Many2one(comodel_name='sale.terms.and.conditions', string="Terms And Conditions")
    conditions_details = fields.Html(string='Conditions Details')
    is_check_display_report = fields.Boolean(string='Display in Report')

    @api.onchange('terms_id')
    def _onchange_conditions_id(self):
        for sale_id in self:
            if sale_id.terms_id:
                sale_id.conditions_details = sale_id.terms_id.condition
