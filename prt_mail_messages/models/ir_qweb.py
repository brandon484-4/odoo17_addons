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

from odoo import api, models
from odoo.tools.profiler import QwebTracker


class IrQWeb(models.AbstractModel):
    _inherit = "ir.qweb"

    # The inherited method is used to regulate the signature location
    @QwebTracker.wrap_render
    @api.model
    def _render(self, template, values=None, **options):
        location = self._context.get("signature_location")
        wizard_mode = self._context.get("default_wizard_mode")
        if wizard_mode not in ["quote", "forward"] or location == "a":
            # Signature Location (Message bottom)
            return super()._render(template, values=values, **options)
        signature = values.pop("signature", False) if location else False
        body = super()._render(template, values=values, **options)
        if signature and location == "b":
            # Signature Location (Before quote)
            quote_index = body.find("<blockquote")
            if quote_index:
                body = "".join((body[:quote_index], signature, body[quote_index:]))
        # Signature Location (No signature)
        return body
