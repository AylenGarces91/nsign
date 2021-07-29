# -*- coding: utf-8 -*-

from odoo import models

class SaleSubscription_reference_custom(models.Model):

    _inherit = 'sale.subscription'

    def _prepare_invoice_line(self, line, fiscal_position, date_start=False, date_stop=False):
        response = super(SaleSubscription_reference_custom, self)._prepare_invoice_line(line, fiscal_position, date_start=False, date_stop=False)
        response['ref'] = self.code if self.code else False;
        return response