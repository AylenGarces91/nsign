# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartnerCustom(models.Model):
    _inherit = 'res.partner'

    x_select_own_bank_values = fields.Many2one('res.partner.bank', string="Banco propio")
