# -*- coding: utf-8 -*-

from odoo import models

class SaleSubscription_reference_custom(models.Model):

    _inherit = 'sale.subscription'

    def _prepare_invoice_line(self, line, fiscal_position, date_start=False, date_stop=False):
        response = super(SaleSubscription_reference_custom, self)._prepare_invoice_line(line, fiscal_position, date_start=False, date_stop=False)
        sale_order = self.env['sale.order'].search([('order_line.subscription_id', 'in', self.ids)], order="id desc", limit=1)
        response['ref'] = sale_order.client_order_ref if sale_order else False;
        return response