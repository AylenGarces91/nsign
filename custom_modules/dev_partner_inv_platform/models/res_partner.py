from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    dev_invoices_platform = fields.Char('Plataforma Facturas')
