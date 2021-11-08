from odoo import models, fields, api


class ProductPackLineInh(models.Model):
    _inherit = 'product.pack.line'

    extra_price_unit = fields.Float('Precio unitario')

    def compute_extra_price(self):
        self.ensure_one()
        self.extra_price_unit = 0
