
from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    @api.multi
    def unlink(self):
        for record in self:
            if move.state == 'draft':
                move.name = '/'
            return super(AccountInvoice, record).unlink()