# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import models, fields, api




class BiHotel(models.Model):
    _name = 'bi.hotel'
    _rec_name = 'hotel_name'
    _description = 'Set Employee Accommodation Hotels'

    hotel_name = fields.Char(string=' Hotel Name',required=True)
    location_id = fields.Many2one('bi.location', string="Location Name",required=True)


