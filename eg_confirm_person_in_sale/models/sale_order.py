from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    confirm_user_id = fields.Many2one(comodel_name="res.partner",string='Confirm By', compute='_compute_confirm_by_sale')

    def _compute_confirm_by_sale(self):
        for sale_id in self:
            sale_id.confirm_user_id = None
            for message_id in sale_id.message_ids:
                if message_id.subtype_id.name == "Sales Order Confirmed":
                    sale_id.confirm_user_id = message_id.create_uid.partner_id.id
