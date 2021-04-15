import base64
import datetime
import json
import logging
from odoo import models, fields, api, _
from requests import request

_logger = logging.getLogger("hubSpot")

class hubspotCredentailDetails(models.Model):
    
    _name = "hubspot.crm"
    _description = "HubSpot CRM"
    
    name = fields.Char("Nombre", required=True)
    hubspot_api_key = fields.Char("HubSpot API Key", required=True, help="Go in the hubspot back office and get Key.")
    
    contact_sync = fields.Boolean(string="Sincronizar Contactos", default=False)
    contact_import = fields.Boolean(string="Importar Contactos", default=False)
    contact_export = fields.Boolean(string="Exportar Contactos", default=False)

    company_sync = fields.Boolean(string="Sincronizar Compañias", default=False)
    company_import = fields.Boolean(string="Importar Compañias", default=False)
    company_export = fields.Boolean(string="Exportar Compañias", default=False)

    product_sync = fields.Boolean(string="Sincronizar Productos", default=False)
    product_import = fields.Boolean(string="Importar Productos", default=False)
    product_export = fields.Boolean(string="Exportar Productos", default=False)

    sale_sync = fields.Boolean(string="Sincronizar Ventas", default=False)
    sale_import = fields.Boolean(string="Importar Ventas", default=False)
    sale_export = fields.Boolean(string="Exportar Ventas", default=False)
    sale_order_id_imported = fields.Char(string="Ultima Venta Importada")

    def create_hubspot_operation(self, operation, operation_type, hubspot_crm_id, log_message):
        vals = {
            'hubspot_operation': operation,
            'hubspot_operation_type': operation_type,
            'hubspot_crm_id': hubspot_crm_id and hubspot_crm_id.id,
            'hubspot_message': log_message,
        }
        operation_id = self.env['hubspot.operation'].create(vals)
        return operation_id

    def create_hubspot_operation_detail(self, operation, operation_type, req_data, response_data, operation_id, fault_operation=False, process_message=False):
        vals = {
            'hubspot_operation': operation,
            'hubspot_operation_type': operation_type,
            'hubspot_request_message': '{}'.format(req_data),
            'hubspot_response_message': '{}'.format(response_data),
            'operation_id': operation_id.id,
            'fault_operation': fault_operation,
            'process_message': process_message,
        }
        operation_detail_id = self.env['hubspot.operation.details'].create(vals)
        return operation_detail_id

    def send_get_request_from_odoo_to_hubspot(self, action, api_url, querystring={}, payloadstring={}):
        try:
            url = "https://api.hubapi.com/crm/v3/%s" % (api_url)
            headers = {
                'accept': "application/json",
                'content-type': "application/json"
            }
            #headers = {'accept': 'application/json'}
            querystring["hapikey"] = self.hubspot_api_key
            payloadstring = json.dumps(payloadstring)

            response_data = request(method=action, url=url, headers=headers, params=querystring, data=payloadstring)
            if response_data.status_code in [200, 201]:
                result = response_data.json()
                _logger.info("hubspot API Response Data : %s" % (result))
                return True, result
            else:
                _logger.info("hubspot API Response Data : %s" % (response_data.text))
                return False, response_data.text
        except Exception as e:
            _logger.info("hubspot API Response Data : %s" % (e))
            return False, e

    def action_contact_import(self):
        contact_obj = self.env['res.partner']
        contact_obj.hubspot_to_odoo_import_contacts(self)
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Contactos importados exitosamente',
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }

    def action_contact_export(self):
        contact_obj = self.env['res.partner']
        contact_obj.hubspot_to_odoo_export_contacts(self)
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Contactos exportados exitosamente',
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }

    def action_company_import(self):
        contact_obj = self.env['res.partner']
        contact_obj.hubspot_to_odoo_import_companies(self)
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Empresas importadas exitosamente',
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }

    def action_company_export(self):
        contact_obj = self.env['res.partner']
        contact_obj.hubspot_to_odoo_export_companies(self)
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Contactos exportados exitosamente',
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }

    def action_product_import(self):
        contact_obj = self.env['product.template']
        contact_obj.hubsport_to_odoo_import_product_all(self)
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Productos importados exitosamente',
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }

    def action_product_export(self):
        contact_obj = self.env['product.template']
        contact_obj.hubsport_to_odoo_export_product_all(self)
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Productos exportados exitosamente',
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }

    def action_sale_import(self):
        sale_obj = self.env['sale.order']
        sale_obj.hubspot_to_odoo_import_orders(self)
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Ventas exportadas exitosamente',
                'img_url': '/web/static/src/img/smile.svg',
                'type': 'rainbow_man',
            }
        }
    
    def convert_date_iso_format(self, dt_str):
        dt, _, us = dt_str.partition(".")
        if us == '':
            dt = dt.replace('Z','')
            us = "0Z"
        dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
        us = int(us.rstrip("Z"), 10)
        return dt + datetime.timedelta(microseconds=us)