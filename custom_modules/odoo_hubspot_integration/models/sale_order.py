from odoo import fields, models, api
import logging
import time

_logger = logging.getLogger(__name__)


class SaleOrder_HubSpot(models.Model):
    
    _inherit = "sale.order"

    hubspot_order_id = fields.Char("Id HubSpot")
    hubspot_order_imported = fields.Boolean(default=False, string="HubSpot es Importado")
    hubspot_pipeline_id = fields.Many2one('hubspot.pipeline', string='Pipeline Id')

    def hubspot_to_odoo_import_orders(self, hubspot_crm=False):
        
        hubspot_operation = hubspot_crm.create_hubspot_operation('order', 'import', hubspot_crm, 'Procesando...')
        self._cr.commit()
        try:
            for pipeline in hubspot_crm.pipeline:
                after = 0
                while True:
                    payload = {
                        "filterGroups":[{
                            "filters":[
                                { "value":pipeline.stage_win,"propertyName":"dealstage","operator":"EQ" },
                                { "value":0,"propertyName":"hs_object_id","operator":"GTE" }
                            ]
                        }],
                        "sorts":[
                            {"direction": "ASCENDING", "propertyName":"hs_object_id"}
                        ],
                        "limit":50,
                        "after":after
                    }
                    order_response_status, order_response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("POST","objects/deals/search",{}, payload)

                    if order_response_status:
                        orders = order_response_data and order_response_data.get('results')

                        for order in orders:
                            order_existing_id = self.env['sale.order'].search([('hubspot_order_id', '=', order.get('id'))], limit=1)

                            if not order_existing_id:
                                date_add = order.get("properties").get("closedate")
                                date_add = hubspot_crm.convert_date_iso_format(date_add)

                                params = {
                                    "properties": ["hs_object_id,amount,closedate,dealname,dealstage,createdate,hs_lastmodifieddate,hubspot_owner_id,pipeline"],
                                    "associations": ["companies,contacts,line_items,products"]
                                }

                                deal_response_status, deal_resp_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("GET", ("objects/deals/%s" % (order.get('id'))), params, {})
                                if(deal_response_status and deal_resp_data):
                                    res_data_asociate = deal_resp_data.get("associations")
                                    company = contact = False

                                    if res_data_asociate is None:
                                        order_message = "El negocio %s no tiene un cliente ni tampoco empresa" % order.get('id')
                                        hubspot_crm.create_hubspot_operation_detail('order', 'import', hubspot_operation, order_response_data, hubspot_operation, False, order_message)
                                        continue

                                    owner_id = False
                                    if deal_resp_data.get('properties').get('hubspot_owner_id'):
                                        owner_id = self.get_owner(hubspot_crm, deal_resp_data.get('properties').get('hubspot_owner_id'))

                                    if res_data_asociate.get("companies", False) and res_data_asociate.get("companies").get("results"):
                                        company = self.env['res.partner'].get_company_data_from_hubspot(hubspot_operation, hubspot_crm, res_data_asociate.get("companies").get("results")[0].get("id"))

                                    if res_data_asociate.get("contacts", False) and res_data_asociate.get("contacts").get("results"):
                                        contact = self.env['res.partner'].get_contact_data_from_hubspot(hubspot_operation, hubspot_crm, res_data_asociate.get("contacts").get("results")[0].get("id"))
                                        # if company:
                                        #     contact.write({'parent_id':company.id})

                                    if not company and not contact:
                                        order_message = "El negocio no tiene un cliente asociado"
                                        hubspot_crm.create_hubspot_operation_detail('order', 'import', hubspot_operation, order_response_data, hubspot_operation, False, order_message)
                                        continue
                                    
                                    order_contact = contact if contact else company
                                    
                                    order_id = self.create_sales_order_from_hubspot(order_contact, date_add, order.get('id'), owner_id, pipeline)
                                    order_id.onchange_partner_id()
                                    order_id.user_id = owner_id
                                    order_message = "{} : Venta Creada".format(order_id.name)
                                    hubspot_crm.create_hubspot_operation_detail('order', 'import', hubspot_operation, order_response_data, hubspot_operation, False, order_message)
                                    
                                    # Order Line Creation Part
                                    if res_data_asociate and res_data_asociate.get("line items"):
                                        line_items_associations = res_data_asociate and res_data_asociate.get("line items").get("results")
                                        
                                        if line_items_associations and order_id:
                                            for order_row in line_items_associations:
                                                line_id = order_row.get('id')
                                                if line_id:
                                                    product_id = self.env['product.template'].hubsport_to_odoo_import_product_single(hubspot_operation, hubspot_crm, line_id)

                                                    line_item = self.get_line_orders_data_from_hubspot(hubspot_crm, line_id)
                                                    quantity = line_item.get("properties").get("quantity") if line_item.get("properties", False) else 0
                                                    price = line_item.get("properties").get("price") if line_item.get("properties", False) else 0
                                                    line = self.create_sale_order_line_from_hubspot(order_id.id, product_id, quantity, price)
                                    
                                    self._cr.commit()
                                    order_message = "Venta importada: %s" % (order_id.name)
                                    hubspot_crm.create_hubspot_operation_detail('order', 'import', hubspot_operation, order, hubspot_operation, True, order_message)
                            else:
                                order_message = "%s : %s : Order Already Exist in Odoo" % (order_existing_id and order_existing_id.name, order.get('id'))
                                hubspot_crm.create_hubspot_operation_detail('order', 'import', hubspot_operation, order, hubspot_operation, True, order_message)

                        if order_response_data.get('paging', False) and order_response_data.get('paging').get('next',False) and order_response_data.get('paging').get('next').get('after',False):
                            after = order_response_data.get('paging').get('next').get('after')
                            time.sleep(5)
                        else:
                            order_message = "Importacion de la etapa %s importado " % (pipeline.stage_win)
                            hubspot_crm.create_hubspot_operation_detail('order', 'import', hubspot_operation, order, hubspot_operation, True, order_message)
                            break

            hubspot_operation and hubspot_operation.write({'hubspot_message': "¡El proceso se completó con éxito!"})
        except Exception as e:
            process_message = "Getting an Error In Import Order Response {}".format(e)
            _logger.info(process_message)
            hubspot_crm.create_hubspot_operation_detail('order', 'import', order_response_data, process_message, hubspot_operation, True, process_message)
            hubspot_operation and hubspot_operation.write({'hubspot_message': "Ocurrio un error!"})
        self._cr.commit()


    def create_sales_order_from_hubspot(self, contact, date_add, sale_id, user_id, pipeline):
        vals = {
            'partner_id': contact.id,
            'partner_invoice_id': contact.id,
            'partner_shipping_id': contact.id,
            'date_order': date_add,
            'user_id': user_id,
            'hubspot_order_id': sale_id,
            'hubspot_order_imported': True,
            'hubspot_pipeline_id': pipeline.id,
            'company_id': pipeline.company_id.id
        }
        return super(SaleOrder_HubSpot, self.env['sale.order']).create(vals)

    def create_sale_order_line_from_hubspot(self, order_id, product_id, quantity, price):
        vals = {
            'order_id': order_id,
            'product_id': product_id.product_variant_id.id,
            'product_uom_qty': quantity,
            'price_unit': price,
            'product_uom': product_id.product_variant_id.uom_id.id
        }
        return self.env['sale.order.line'].create(vals)
    
    def get_line_orders_data_from_hubspot(self, hubspot_crm, line_id):
        if(line_id):
            params = {
                "properties": ["name,quantity,price,hs_sku,hs_product_id,hs_recurring_billing_period"]
            }            
            response_status, response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("GET", "objects/line_items/%s" % (line_id), params, {})
            if(response_status and response_data):
                _logger.info("hubspot Get Order Response : {0}".format(response_data))
                return response_data
        return False

    def get_owner(self, hubspot_crm, hubspot_owner_id):
        response_status, response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("GET",("owners/%s" % hubspot_owner_id))
        user_id = self.env['ir.config_parameter'].sudo().get_param('x_user_admin_id')

        if response_status and response_data.get('email', False):
            user = self.env['res.users'].search([('email','=',response_data.get('email')),('groups_id','=',8)], limit=1)
            if user:
                return user.id
            else:
                #return self.env['res.users'].search([('partner_id','=',self.env.company.partner_id.id)], limit=1).id
                return self.env['res.users'].search([('id','=',user_id)], limit=1).id
        else:
            return self.env['res.users'].search([('id','=',user_id)], limit=1).id
            # return self.env['res.users'].search([('partner_id','=',self.env.company.partner_id.id)], limit=1).id
        