from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    dev_sent_platform = fields.Boolean('¿Enviado a plataforma?', default=False)
    dev_partner_invoices_platform = fields.Char(
        'Plataforma del Cliente',
        related='partner_id.dev_invoices_platform')
