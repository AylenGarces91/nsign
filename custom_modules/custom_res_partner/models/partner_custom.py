# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class PartnerCustom(models.Model):
    _inherit = 'res.partner'

    x_purchase_order_number_mandatory = fields.Boolean(string="Número de pedido de compra obligatorio")
