from odoo import fields, models, api
from datetime import datetime, timedelta
import logging
import json

_logger = logging.getLogger("hubspot")


class SaleOrder_HubSpot(models.Model):
    
    _inherit = "sale.order"

    hubspot_order_id = fields.Char("HubSpot Id", copy=False)
    hubspot_order_imported = fields.Boolean(default=False, string="HubSpot es Importado", copy=False)
    hubspot_crm_id = fields.Many2one('hubspot.crm', string="HubSpot Id")

    def hubspot_to_odoo_import_orders(self, hubspot_crm=False):
        
        hubspot_operation = hubspot_crm.create_hubspot_operation('order', 'import', hubspot_crm, 'Procesando...')
        self._cr.commit()
        try:
            last_order_id = hubspot_crm.sale_order_id_imported if hubspot_crm.sale_order_id_imported else 0

            payload = {
                "filterGroups":[{
                    "filters":[
                        { "value":"closedwon","propertyName":"dealstage","operator":"EQ" },
                        { "value":last_order_id,"propertyName":"hs_object_id","operator":"GTE" }
                    ]
                }],
                "sorts":[
                    {"direction": "ASCENDING", "propertyName":"hs_object_id"}
                ],
                "limit":50,
                "after":0
            }

            order_response_status, order_response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("POST","objects/deals/search",{}, payload)
            if order_response_status:
                orders = order_response_data and order_response_data.get('results')

                for order in orders:
                    try:
                        sale_id = order.get('id')
                        order_existing_id = self.env['sale.order'].search([('hubspot_order_id', '=', sale_id)], limit=1)
                       
                        if not order_existing_id:
                            date_add = order.get("properties").get("closedate")
                            date_add = hubspot_crm.convert_date_iso_format(date_add)

                            params = {
                                "properties": ["hs_object_id,amount,closedate,dealname,dealstage,createdate,hs_lastmodifieddate,hubspot_owner_id,pipeline"],
                                "associations": ["companies,contacts,line_items,products"]
                            }

                            deal_response_status, deal_resp_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("GET", ("objects/deals/%s" % (sale_id)), params, {})
                            if(deal_response_status and deal_resp_data):
                                res_data_asociate = deal_resp_data.get("associations")
                                contact_id = company_id = contact = company = False

                                if res_data_asociate.get("contacts", False) and res_data_asociate.get("contacts").get("results"):
                                    contact_id = res_data_asociate.get("contacts").get("results")[0].get("id")

                                if res_data_asociate.get("companies", False) and res_data_asociate.get("companies").get("results"):
                                    company_id = res_data_asociate.get("companies").get("results")[0].get("id")

                                #obtenemos datos del contacto y empresa en odoo
                                if contact_id:
                                    contact = self.env['res.partner'].search([('hubspot_contact_id', '=', response_data.get('id')),('is_company','=',False)], limit=1)
                                    # contact = self.env['res.partner'].get_contact_data_from_hubspot(hubspot_crm, contact_id)
                                if company_id:
                                    contact = self.env['res.partner'].search([('hubspot_contact_id', '=', response_data.get('id')),('is_company','=',True)], limit=1)
                                    # company = self.env['res.partner'].get_company_data_from_hubspot(hubspot_crm, company_id)
                                

                                if not contact:
                                    order_message = "El negocio no tiene un cliente asociado"
                                    hubspot_crm.create_hubspot_operation_detail('order', 'import', hubspot_operation, order_response_data, hubspot_operation, False, order_message)
                                    continue

                                try:
                                    order_id = self.create_sales_order_from_hubspot(contact, date_add, sale_id, hubspot_crm)
                                    order_message = "{} : Venta Creada".format(order_id.name)
                                    hubspot_crm.create_hubspot_operation_detail('order', 'import', hubspot_operation, order_response_data, hubspot_operation, False, order_message)
                                except Exception as e:
                                    process_message = "Getting an Error In Create Order procecss {}".format(e)
                                    hubspot_crm.create_hubspot_operation_detail('order', 'import', '', '', hubspot_operation, True, process_message)
                                
                                # Order Line Creation Part
                                line_items_associations = res_data_asociate and res_data_asociate.get("line items").get("results")
                                
                                if line_items_associations and order_id:
                                   for order_row in line_items_associations:
                                     line_id = order_row.get('id')
                                     if line_id:
                                        product_id = self.env['product.template'].hubsport_to_odoo_import_product_single(hubspot_crm, line_id)

                                        line_item = self.get_line_orders_data_from_hubspot(hubspot_crm, line_id)
                                        quantity = line_item.get("properties").get("quantity") if line_item.get("properties", False) else 0
                                        price = line_item.get("properties").get("price") if line_item.get("properties", False) else 0
                                        line = self.create_sale_order_line_from_hubspot(order_id.id, product_id, quantity, price)
                        else:
                            order_message = "%s : %s : Order Already Exist in Odoo" % (order_existing_id and order_existing_id.name, sale_id)
                            hubspot_crm.create_hubspot_operation_detail('order', 'import', hubspot_operation, order, hubspot_operation, True, order_message)

                        self._cr.commit()
                        hubspot_operation and hubspot_operation.write({'hubspot_message': "¡El proceso se completó con éxito!"})
                        
                    except Exception as e:
                        process_message = "Getting An Error In Import Order Response".format(e)
                        hubspot_crm.create_hubspot_operation_detail('order', 'import', '', '', hubspot_operation, True, process_message)
                hubspot_operation and hubspot_operation.write({'hubspot_message': "¡El proceso se completó con éxito!"})
        except Exception as e:
            process_message = "Getting an Error In Import Order Response {}".format(e)
            _logger.info(process_message)
            hubspot_crm.create_hubspot_operation_detail('order', 'import', order_response_data, process_message, hubspot_operation, True, process_message)
            hubspot_operation and hubspot_operation.write({'hubspot_message': "Ocurrio un error!"})
        self._cr.commit()


    def create_sales_order_from_hubspot(self, contact, date_add, sale_id, hubspot_crm):
        vals = {
            'partner_id': contact.id,
            'partner_invoice_id': contact.id,
            'partner_shipping_id': contact.id,
            'date_order': date_add,
            'hubspot_order_id': sale_id,
            'hubspot_order_imported': True,
            'hubspot_crm_id': hubspot_crm.id
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