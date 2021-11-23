from odoo import models, fields, api


class StockPickingInh(models.Model):
    _inherit = 'stock.picking'

    total_sale = fields.Monetary('Total', compute='_compute_total_sale')
    currency_id = fields.Many2one(
        'res.currency', string='Company currency', compute="_comp_currency_id")

    @api.depends('company_id')
    def _comp_currency_id(self):
        for picking in self:
            currency = False
            for move in picking.move_ids_without_package:
                if move.sale_line_id.id:
                    currency = move.sale_line_id.order_id.currency_id
                    break
            picking.currency_id = currency.id if currency is not False else picking.company_id.currency_id.id

    @api.depends('currency_id')
    def _compute_total_sale(self):
        for picking in self:
            amounts = [
                l.sale_line_id.price_subtotal for l in picking.move_ids_without_package if l.sale_line_id.id]
            picking.total_sale = sum(amounts)

    def write(self, vals):
        res = super(StockPickingInh, self).write(vals)
        self.write_date_done(vals.get('date_done', False))
        return res

    def write_date_done(self, date_done):
        if date_done is not False:
            for move_line in self.move_line_ids_without_package:
                move_line.update({'date': date_done})
        print('Stock move lines updated to {0}'.format(date_done))
