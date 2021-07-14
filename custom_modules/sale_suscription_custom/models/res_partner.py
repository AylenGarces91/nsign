# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ResPartner_newfields_custom(models.Model):

    _inherit = 'res.partner'

    x_reseller = fields.Boolean("Reseller")