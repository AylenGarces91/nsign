# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ContactNifFilterCustom(models.Model):

    _inherit = 'res.partner'
    x_contact_nif_filter = fields.Many2one('res.partner', string='contact_nif', readonly=True)
