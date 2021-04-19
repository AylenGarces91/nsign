from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class ResUser_HubSpot(models.Model):

    _inherit = "res.users"

    hubspot_user_id = fields.Char("HubSpot User Id")
    hubspot_user_imported = fields.Boolean(default=False, string="HubSpot es Importado")
    hubspot_crm_id = fields.Many2one('hubspot.crm', string="HubSpot Id")


    def get_user_data_from_hubspot(self, hubspot_crm, hubspot_user_id, hubspot_operation):
        self._cr.commit()
        try:
            querystring = { "idProperty":"id","archived":"false" }
            response_status, response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("GET",("owners/%s" % hubspot_user_id), querystring)
            if response_status:
                
                user = self.env['res.users'].search([('hubspot_user_id', '=', response_data.get('id'))], limit=1)
                if not user:
                    user = self.env['res.users'].search([('login', '=', response_data.get('email'))], limit=1)

                if not user:
                    user = self.env['res.users'].create({
                        'name': response_data.get('firstName','') + " " + response_data.get('lastName',''),
                        'login': response_data.get('email',False),
                        'hubspot_user_id': response_data.get('id'),
                        'hubspot_user_imported': True,
                        'hubspot_crm_id': hubspot_crm.id
                    })
                    process_message = "Usuario Creado: {0}".format(user.name)
                else:
                    fecha_modificacion = response_data.get('updatedAt')
                    fecha_modificacion = hubspot_crm.convert_date_iso_format(fecha_modificacion)
                    if fecha_modificacion > user.write_date:
                        user.write({
                            'name': response_data.get('firstName','') + " " + response_data.get('lastName',''),
                            'login': response_data.get('email',False),
                            'hubspot_contact_id': response_data.get('id'),
                        })
                        process_message = "Usuario Actualizado: {0}".format(user.name)
                    else:
                        process_message = "Usuario no actualizado por fecha de modificación: {0}".format(user.name)
                    
                hubspot_crm.create_hubspot_operation_detail('user', 'import', False, response_data, hubspot_operation, False, process_message)
                self._cr.commit()
            else:
                process_message = "Error en la respuesta de importación de Usuario {}".format(response_data)
                hubspot_crm.create_hubspot_operation_detail('user','import','',response_data,hubspot_operation,True,process_message)
            
            hubspot_operation.write({'hubspot_message': "¡El proceso de importar usuario se completó con éxito!"})
        except Exception as e:
            process_message="Error en la respuesta de importación de usuario {}".format(e)
            _logger.info(process_message)
            hubspot_crm.create_hubspot_operation_detail('contactuser_company','import',response_data,process_message,hubspot_operation,True,process_message)
            hubspot_operation.write({'hubspot_message': "El proceso aún no está completo, ocurrio un Error! %s" % (e)})
        self._cr.commit()
        return user

