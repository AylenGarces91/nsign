# -*- coding: utf-8 -*-
from odoo import fields, models, api


class InvoiceReportCustom(models.Model):

    _inherit = 'account.invoice.report'

    x_product_total_cost_amount = fields.Float(string='Importe Coste', readonly=True)
    x_product_total_cost = fields.Float(string='Coste', readonly=True)
    x_product_total_qty = fields.Float(string='Cantidad', readonly=True)

    def _select(self):
        return super()._select() + ", line.quantity AS x_product_total_qty, prop.value_float AS x_product_total_cost, sum(line.quantity * prop.value_float) AS x_product_total_cost_amount"

    def _group_by(self):
        return super()._group_by() + ", invoice_product.id, ptemp.id, prop.id"

    def _from(self):
        return super()._from() + " LEFT JOIN product_product invoice_product ON invoice_product.id = line.product_id LEFT JOIN product_template AS ptemp ON invoice_product.product_tmpl_id = ptemp.id LEFT JOIN ir_property prop on prop.res_id = 'product.product, || invoice_product.id'" 