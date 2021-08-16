
from odoo import models, fields, api


class AccountInvoice(models.Model):
    _inherit = 'account.move'
    
    def unlink(self):
        for record in self:
            if record.state == 'draft':
                record.name = '/'
            return super(AccountInvoice, record).unlink()