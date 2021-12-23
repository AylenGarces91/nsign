# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AccountMoveCustom(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        partner = self.env['res.partner'].search([('id', '=', vals['partner_id'])])
       
        if partner and partner.x_purchase_order_number_mandatory and self.state is False:
            raise UserError("No es posible realizar la Factura, es obligatorio para este usuario disponer del numero de pedido de compra para poder realizar la factura de venta.")
        else:
            super(AccountMoveCustom, self).create(vals)
