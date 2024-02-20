###################################################################################
#
#    Copyright (C) 2020 Cetmix OÜ
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

from odoo import api, fields, models


class CxModelReference(models.Model):
    _name = "cx.model.reference"
    _description = "Referable Models"
    _order = "sequence"

    _sql_constraints = [
        ("model_unique", "UNIQUE(ir_model_id)", "Model name must be unique!")
    ]

    def _domain_ir_model_id(self):
        ir_model_ids = self.search([]).mapped("ir_model_id").ids
        return [("id", "not in", ir_model_ids), ("transient", "=", False)]

    sequence = fields.Integer(default=10)
    ir_model_id = fields.Many2one(
        comodel_name="ir.model",
        string="Model",
        domain=lambda self: self._domain_ir_model_id(),
        required=True,
        ondelete="cascade",
    )
    custom_name = fields.Char(string="Display Name", translate=True, required=True)
    model = fields.Char(string="Technical Name", related="ir_model_id.model")

    @api.onchange("ir_model_id")
    def onchange_ir_model_id(self):
        """
        At change 'ir_model_id' field
        set custom name by default
        """
        if self.ir_model_id:
            self.custom_name = self.ir_model_id.name

    @api.model
    def referenceable_models(self):
        IrModelAccess = self.env["ir.model.access"].with_user(self.env.user.id)
        return [
            (x.model, x.custom_name)
            for x in self.search([])
            if IrModelAccess.check(x.model, "read", False)
        ]
