from odoo import models, fields, api


class SaleOrderLineInh(models.Model):
    _inherit = 'sale.order.line'

    price_pack = fields.Monetary('Precio Kit')
    price_pack_subtotal = fields.Monetary(
        'Subtotal Kit', compute='_compute_price_pack', store=True)

    @api.depends('price_pack')
    def _compute_price_pack(self):
        for line in self:
            price = line.price_pack * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id,
                                            line.product_uom_qty,
                                            product=line.product_id,
                                            partner=line.order_id.partner_shipping_id)
            line.update({
                'price_pack_subtotal': taxes['total_included'],
            })

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record.product_id.pack_ok:
            price_unit = record.product_id.list_price
            # Uncomment to use static_pack_price
            # price_unit = record.product_id.product_pack_price
            record.update({'price_unit': 0, 'price_pack': price_unit})
        if record.pack_parent_line_id.id:
            for pack_line in record.pack_parent_line_id.product_id.pack_line_ids:
                if pack_line.product_id.id == record.product_id.id:
                    record.write({'price_unit': pack_line.extra_price_unit})
        return record

    def write(self, vals):
        if self.product_id.pack_ok:
            vals['price_unit'] = 0
            vals['price_pack'] = self.product_id.list_price
            # uncomment to use static_pack_price
            # vals['price_pack'] = self.product_id.product_pack_price
        if self.pack_parent_line_id.id:
            for pack_line in self.pack_parent_line_id.product_id.pack_line_ids:
                if pack_line.product_id.id == self.product_id.id:
                    vals['price_unit'] = pack_line.extra_price_unit
        res = super().write(vals)
        return res
