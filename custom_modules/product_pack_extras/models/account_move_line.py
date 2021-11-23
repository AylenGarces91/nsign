from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_packdetail = fields.Boolean(
        'Pack', _compute='_compute_pack_parent')

    pack_sale_line_ids = fields.Many2many('sale.order.line',
                                          'sale_order_line_invoice_rel',
                                          'invoice_line_id',
                                          'order_line_id',
                                          string='Sale Lines',
                                          copy=False)

    def _compute_pack_parent(self):
        for line in self:
            is_packdetail = False
            for sale_line in line.pack_sale_line_ids:
                if sale_line.pack_parent_line_id.id:
                    line.is_packdetail = True
                    break
            line.pack_parent_line_id = is_packdetail
