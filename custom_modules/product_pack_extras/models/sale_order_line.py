from odoo import models, api


class SaleOrderLineInh(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record.product_id.pack_ok:
            record.update({'price_unit': 0})
        if record.pack_parent_line_id.id:
            for pack_line in record.pack_parent_line_id.product_id.pack_line_ids:
                if pack_line.product_id.id == record.product_id.id:
                    record.write({'price_unit': pack_line.extra_price_unit})
        return record

    def write(self, vals):
        if self.pack_parent_line_id.id:
            for pack_line in self.pack_parent_line_id.product_id.pack_line_ids:
                if pack_line.product_id.id == self.product_id.id:
                    vals['price_unit'] = pack_line.extra_price_unit
        res = super().write(vals)
        return res
