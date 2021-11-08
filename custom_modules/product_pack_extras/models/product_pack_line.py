from odoo import models, fields, api


class ProductPackLineInh(models.Model):
    _inherit = 'product.pack.line'

    extra_price_unit = fields.Float('Precio unitario', store=True)

    def compute_extra_price(self):
        for record in self:
            precio = record.product_id.list_price
            # Uncomment to use static_pack_price
            # precio = record.product_id.product_pack_price
            precio_kit = record.parent_product_id.list_price
            sum_precios = record.parent_product_id.get_pack_prices_sum()
            price_unit = precio * (precio_kit / sum_precios)
            record.extra_price_unit = price_unit / record.quantity
