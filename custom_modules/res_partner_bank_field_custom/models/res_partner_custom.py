# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartnerCustom(models.Model):
    _inherit = 'res.partner'
        
    #     return bank_list
    x_select_own_bank_values = fields.Many2one('account.journal', string="Banco propio", domain="[('x_is_own_bank_value', '=', True)]", stored=True)   
