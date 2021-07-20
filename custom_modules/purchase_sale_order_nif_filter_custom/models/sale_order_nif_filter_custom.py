# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrderNifFilterCustom(models.Model):

    _inherit = 'sale.order'
    x_sale_order_nif_filter = fields.Many2one('sale.order', 'Sector', readonly=True)
