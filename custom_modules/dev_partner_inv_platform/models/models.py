from odoo import models, fields, api


class DevPartner(models.Model):
    _name = 'dev.model'

    name = fields.Char('Name', required=True)

    @api.model
    def create(self, vals):
        # Execute before saving
        res = super(DevModel, self).create(vals)
        # execute after saving
        return res

    def single_action(self):
        self.ensure_one()
        print(self.name)
