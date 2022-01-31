# -*- coding: utf-8 -*-
from odoo import fields, models, api


class SaleOrderCustom(models.Model):

    _inherit = "sale.order.line"

    x_cost_amount = fields.Float(string='Importe Coste', compute="_cost_amount_value", help="coste por cantidad")

    @api.depends('product_uom_qty')
    def _cost_amount_value(self):
        for rec in self:
            rec.x_cost_amount = 0.00
            if rec.purchase_price:
                rec.x_cost_amount = rec.purchase_price * rec.product_uom_qty    
