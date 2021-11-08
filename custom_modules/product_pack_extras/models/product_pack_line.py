from odoo import models, fields, api


class ProductPackLineInh(models.Model):
    _inherit = 'product.pack.line'

    extra_price_unit = fields.Float(
        'Precio unitario', compute='_compute_extra_price')

    def _compute_extra_price(self):
        for record in self:
            precio = record.product_id.list_price
            precio_kit = record.parent_product_id.list_price
            sum_precios = record.parent_product_id.get_pack_prices_sum()
            price_unit = precio * (precio_kit / sum_precios)
            record.extra_price_unit = price_unit / record.quantity



class ProductProductInh(models.Model):
    _inherit = 'product.product'

    def get_pack_prices_sum(self):
        prices = [x.product_id.list_price for x in self.pack_line_ids]
        return sum(prices)
