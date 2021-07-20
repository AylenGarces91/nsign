# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PurchaseOrderNifFilterCustom(models.Model):
    
    _inherit = 'purchase.order'
    x_purchase_order_nif_filter = fields.Many2one('purchase.order', 'Sector', readonly=True)
