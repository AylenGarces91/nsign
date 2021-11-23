from odoo import models, fields, api


class StockPickingInh(models.Model):
    _inherit = 'stock.picking'

    def write(self, vals):
        res = super(StockPickingInh, self).write(vals)
        self.write_date_done(vals.get('date_done', False))
        return res
    

    def write_date_done(self, date_done):
        if date_done is not False:
            for move_line in self.move_line_ids_without_package:
                move_line.update({'date': date_done})
        print('Stock move lines updated to {0}'.format(date_done))
