 # -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartnerBankCustom(models.Model):
    _inherit = 'res.partner.bank'
    
    x_is_own_bank_value = fields.Boolean(string="Es banco propio", store=True, help='Si la cuenta bancaria es diferente de la cuenta habitual de BANKINTER.')
