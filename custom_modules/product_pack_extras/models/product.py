from odoo import models, api, fields


class ProductTemplateInh(models.Model):
    _inherit = 'product.template'

    # static_pack_price Prepared in case of static price required 
    # product_pack_price = fields.Monetary('Precio Kit')
    
    @api.onchange('pack_line_ids')
    def onchange_pack_lines_extra(self):
        for record in self:
            precio_kit = record.list_price
            # Uncomment to use static_pack_price
            # precio_kit = record.product_id.product_pack_price
            prices = [x.product_id.list_price for x in self.pack_line_ids]
            sum_precios = sum(prices) if sum(prices) != 0 else 1
            divisor_ponderado = precio_kit / sum_precios
            for line in record.pack_line_ids:
                precio = line.product_id.list_price
                price_unit = precio * (divisor_ponderado)
                line.extra_price_unit = price_unit / line.quantity