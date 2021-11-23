from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_packdetail = fields.Boolean('Pack', compute='_compute_pack_parent')

    pack_sale_line_ids = fields.Many2many('sale.order.line',
                                          'sale_order_line_invoice_rel',
                                          'invoice_line_id',
                                          'order_line_id',
                                          string='Sale Lines',
                                          copy=False)
    price_pack_subtotal = fields.Monetary('pack Subtotal', compute='_compute_pack_prices')
    price_pack = fields.Monetary('pack Price', compute='_compute_pack_prices')

    def _compute_pack_parent(self):
        for line in self:
            is_packdetail = False
            for sale_line in line.pack_sale_line_ids:
                if sale_line.pack_parent_line_id.id:
                    is_packdetail = True
                    break
            line.is_packdetail = is_packdetail

    def _compute_pack_prices(self):
        for line in self:
            price_pack_subtotal, price_pack = 0, 0
            for sale_line in line.pack_sale_line_ids:
                if sale_line.price_pack:
                    price_pack_subtotal = sale_line.price_pack_subtotal
                    price_pack = sale_line.price_pack
                    break
            line.price_pack = price_pack
            line.price_pack_subtotal = price_pack_subtotal