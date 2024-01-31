# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import models, fields, api


class BiLocation(models.Model):
    _name = 'bi.location'
    _rec_name = 'location_name'
    _description = 'Set Employee Accommodation Location'

    location_name = fields.Char(string=' Location Name',required=True,tracking=True)