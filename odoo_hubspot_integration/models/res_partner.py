from odoo import fields, models, api
import logging

_logger = logging.getLogger(__name__)


class ResPartner_HubSpot(models.Model):

    _inherit = "res.partner"

    hubspot_contact_id = fields.Char("HubSpot Contact Id")
    hubspot_contact_imported = fields.Boolean(default=False, string="HubSpot es Importado")
    hubspot_crm_id = fields.Many2one('hubspot.crm', string="HubSpot Id")
    hubspot_write_date = fields.Datetime(string="HubSpot Fecha Modificación")


    @api.model_create_multi
    def create(self, vals_list):
        partners = super(ResPartner_HubSpot, self).create(vals_list)
        ################################################################
        hubspot_crm = self.env['hubspot.crm'].search([('id','!=',False)], limit=1)
        if hubspot_crm.contact_crud:
            self._cr.commit()
            try:
                self.contact_sincronize(partners)
            except Exception as e:
                _logger.info("Error al exportar hacia hubspot {}".format(e))
        ################################################################
        return partners


    def write(self, vals):
        partners = super(ResPartner_HubSpot, self).write(vals)
        ################################################################
        hubspot_crm = self.env['hubspot.crm'].search([('id','!=',False)], limit=1)
        if hubspot_crm.contact_crud:
            self._cr.commit()
            try:
                if partners == True:
                    contact = self.env['res.partner'].search([('id','=',self.id)])
                    self.contact_sincronize(contact)
            except Exception as e:
                _logger.info("Error al exportar hacia hubspot {}".format(e))
        ################################################################
        return partners

    def contact_sincronize(self, contact):
        try:
            hubspot_crm = self.env['hubspot.crm'].search([('id','!=',False)], limit=1)
            if contact.is_company == True:
                hubspot_operation = hubspot_crm.create_hubspot_operation('contact_company','export',hubspot_crm,'Procesando...')
                payload = {
                    "properties":{
                        "name": contact.name,
                        "phone": contact.phone or "",
                        "website": contact.website or "",
                        "address": contact.street or "",
                        "city": contact.city or "",
                        "country": contact.country_id.name if contact.country_id else "",
                        "state": contact.state_id.name if contact.state_id else "",
                        "zip": contact.zip or "",
                        "domain": contact.website or "",
                        "industry": contact.category_id.name or ""
                    }
                }
                                
                if not contact.hubspot_contact_id:
                    response_status, response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("POST","objects/companies",{}, payload)
                else:
                    response_status, response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("PATCH","objects/companies/%s" % contact.hubspot_contact_id,{}, payload)
                
                if response_status:
                    fecha_modificacion = response_data.get('properties').get('hs_lastmodifieddate')
                    fecha_modificacion = hubspot_crm.convert_date_iso_format(fecha_modificacion)

                    super(ResPartner_HubSpot, contact).write({
                        'hubspot_contact_id': response_data.get('id'),
                        'hubspot_crm_id': hubspot_crm.id,
                        'hubspot_write_date': fecha_modificacion,
                    })
                    process_message = "Compañia creado en hubspot: {}".format(contact.name)
                else:
                    process_message = "Error en la exportación de la compañia {}".format(contact.name)
                    hubspot_crm.create_hubspot_operation_detail('customer','export',response_data,process_message,hubspot_operation,True,process_message)
                    hubspot_operation.write({'hubspot_message': "El proceso aún no está completo, ocurrio un Error! %s" % (process_message)})
            else:
                hubspot_operation = hubspot_crm.create_hubspot_operation('customer','export',hubspot_crm,'Procesando...')
                payload = {
                    "properties":{
                        "firstname": contact.name,
                        "lastname": "",
                        "email": contact.email or "",
                        "phone": contact.phone or "",
                        "mobile": contact.mobile or "",
                        "website": contact.website or "",
                        "address": contact.street or "",
                        "city": contact.city or "",
                        "country": contact.country_id.name if contact.country_id else "",
                        "state": contact.state_id.name if contact.state_id else "",
                        "zip": contact.zip or "",
                        "company": contact.company_name or ""
                        }
                    }
                                
                if not contact.hubspot_contact_id:
                    response_status, response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("POST","objects/contacts",{}, payload)
                else:
                    response_status, response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("PATCH","objects/contacts/%s" % contact.hubspot_contact_id,{}, payload)

                if response_status:
                    fecha_modificacion = response_data.get('properties').get('lastmodifieddate')
                    fecha_modificacion = hubspot_crm.convert_date_iso_format(fecha_modificacion)

                    super(ResPartner_HubSpot, contact).write({
                        'hubspot_contact_id': response_data.get('id'),
                        'hubspot_crm_id': hubspot_crm.id,
                        'hubspot_write_date': fecha_modificacion,
                    })
                    process_message = "Contacto creado en hubspot: {}".format(contact.name)
                else:
                    process_message = "Error en la exportación del contacto {}".format(contact.name)
                    hubspot_crm.create_hubspot_operation_detail('customer','export',response_data,process_message,hubspot_operation,True,process_message)
                    hubspot_operation.write({'hubspot_message': "El proceso aún no está completo, ocurrio un Error! %s" % (process_message)})


            process_message = "El proceso de exportacion se realizo correctamente"
            hubspot_crm.create_hubspot_operation_detail('contact_company', 'export', True, '', hubspot_operation, False, process_message)
            self._cr.commit()
        except Exception as e:
            process_message="Error en la respuesta de importación de contacto {}".format(e)
            _logger.info(process_message)
            hubspot_crm.create_hubspot_operation_detail('contact_company','import',response_data,process_message,hubspot_operation,True,process_message)
            hubspot_operation.write({'hubspot_message': "El proceso aún no está completo, ocurrio un Error! %s" % (e)})
        self._cr.commit()


    def hubspot_to_odoo_import_companies(self, hubspot_crm = False):
        hubspot_operation = hubspot_crm.create_hubspot_operation('contact_company','import',hubspot_crm,'Procesando...')
        self._cr.commit()
        try:
            after = 0
            while True:
                payload = {
                    "filterGroups":[{
                        "filters":[
                            {"propertyName": "name", "operator": "HAS_PROPERTY"},
                        ]
                    }],
                    "sorts":[
                        {"direction": "ASCENDING", "propertyName":"hs_object_id"}
                    ],
                    "properties":["hs_object_id,name,zip,address,phone,industry,website,country,city,state"],
                    "associations":["contacts"],
                    "limit":50,
                    "after":after
                }
                response_status, response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("POST","objects/companies/search",{}, payload)

                if response_status:
                    for company in response_data.get('results',[]):
                        company_info = self.env['res.partner'].search([('hubspot_contact_id','=',company.get('id')),('is_company','=',True)], limit=1)
                        if not company_info:
                            company_info = self.env['res.partner'].search([('is_company','=',True),('name','=',company.get('properties').get('name'))], limit=1)

                        # country = company.get('properties').get('country',False) if company.get('properties').get('country') is not None else False
                        # country_id = self.env['res.country'].search([('name', 'like', country[0])], limit=1) if country else False
                        
                        # state = company.get('properties').get('state',False) if company.get('properties').get('state') is not None else False
                        # state_id = self.env['res.country.state'].search([('code', 'like', state[0])], limit=1) if state else False

                        fecha_modificacion = company.get('properties').get('hs_lastmodifieddate')
                        fecha_modificacion = hubspot_crm.convert_date_iso_format(fecha_modificacion)

                        if not company_info:
                            #creamos la compania
                            contact_company = super(ResPartner_HubSpot, self).create({
                                'name': company.get('properties').get('name'),
                                'phone': company.get('properties').get('phone',False),
                                'website': company.get('properties').get('website',False),
                                'street': company.get('properties').get('address',False),
                                'city': company.get('properties').get('city',False),
                                # 'country_id': country_id.id if country_id else False,
                                # 'state_id': state_id.id if state_id else False,
                                'zip': company.get('properties').get('zip',False),
                                'is_company': True,
                                'hubspot_contact_id': company.get('properties').get('hs_object_id'),
                                'hubspot_contact_imported': True,
                                'hubspot_crm_id': hubspot_crm.id,
                                'hubspot_write_date': fecha_modificacion,
                            })
                            process_message = "Contacto Compañia Creado: {0}".format(contact_company.name)
                        else:
                            if company_info.hubspot_write_date and fecha_modificacion > company_info.hubspot_write_date:
                                # editamos la compania en odoo
                                super(ResPartner_HubSpot, company_info).write({
                                    'name': company.get('properties').get('name'),
                                    'phone': company.get('properties').get('phone',False),
                                    'website': company.get('properties').get('website',False),
                                    'street': company.get('properties').get('address',False),
                                    'city': company.get('properties').get('city',False),
                                    #'country_id': country_id.id if country_id else False,
                                    #'state_id': state_id.id if state_id else False,
                                    'zip': company.get('properties').get('zip',False),
                                    'is_company': True,
                                    'hubspot_contact_id': company.get('properties').get('hs_object_id'),
                                    'hubspot_contact_imported': True,
                                    'hubspot_crm_id': hubspot_crm.id,
                                    'hubspot_write_date': fecha_modificacion,
                                })
                                process_message = "Compañia Actualizada: {0}".format(company_info.name)
                            else:
                                process_message = "Compañia no es necesario actualizar por fecha de modificación: {0}".format(company_info.name)

                        hubspot_crm.create_hubspot_operation_detail('contact_company', 'import', True, response_data, hubspot_operation, False, process_message)
                        self._cr.commit()

                    if response_data.get('paging', False) and response_data.get('paging').get('next',False) and response_data.get('paging').get('next').get('after',False):
                        after = response_data.get('paging').get('next').get('after')
                    else:
                        break
                else:
                    process_message = "Error en la respuesta de importación de Empresas {}".format(response_data)
                    hubspot_crm.create_hubspot_operation_detail('customer','import','',response_data,hubspot_operation,True,process_message)
                    break

            hubspot_operation.write({'hubspot_message': "¡El proceso de importar compañia se completó con éxito!"})
        except Exception as e:
            process_message="Error en la respuesta de importación de la compania {}".format(e)
            _logger.info(process_message)
            hubspot_crm.create_hubspot_operation_detail('contact_company','import',response_data,process_message,hubspot_operation,True,process_message)
            hubspot_operation.write({'hubspot_message': "El proceso aún no está completo, ocurrio un Error! %s" % (e)})
        self._cr.commit()

    def hubspot_to_odoo_export_companies(self, hubspot_crm):
        hubspot_operation = hubspot_crm.create_hubspot_operation('contact_company','export',hubspot_crm,'Procesando...')
        self._cr.commit()
        try:
            companies = self.env['res.partner'].search([('hubspot_contact_id','=',False),('active','=', True),('is_company','=',True)])
            if companies:
                for company in companies:
                    payload = {
                       "properties":{
                       "name": company.name,
                       "phone": company.phone or "",
                       "state": company.state_id.name or "",
                       "domain": company.website or "",
                       "industry": company.category_id.name or ""
                        }
                    }
                    response_status, response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("POST","objects/companies",{}, payload)
                    if response_status:
                        
                        fecha_modificacion = response_data.get('properties').get('hs_lastmodifieddate')
                        fecha_modificacion = hubspot_crm.convert_date_iso_format(fecha_modificacion)
                        super(ResPartner_HubSpot, company).write({
                           'hubspot_contact_id': response_data.get('id'),
                           'hubspot_crm_id': hubspot_crm.id,
                           'hubspot_write_date': fecha_modificacion,
                        })
                        process_message = "Compañia creado en hubspot: {}".format(company.company_id.name)
                    else:
                        process_message = "Error en la exportación del contacto {}".format(company.company_id.name)
                        hubspot_crm.create_hubspot_operation_detail('customer','export',response_data,process_message,hubspot_operation,True,process_message)
                        hubspot_operation.write({'hubspot_message': "El proceso aún no está completo, ocurrio un Error! %s" % (process_message)})
            process_message = "El proceso de exportacion se realizo correctamente"
            hubspot_crm.create_hubspot_operation_detail('contact_company', 'export', True, '', hubspot_operation, False, process_message)
            self._cr.commit()
        except Exception as e:
            process_message="Error en la respuesta de importación de contacto {}".format(e)
            _logger.info(process_message)
            hubspot_crm.create_hubspot_operation_detail('contact_company','import',response_data,process_message,hubspot_operation,True,process_message)
            hubspot_operation.write({'hubspot_message': "El proceso aún no está completo, ocurrio un Error! %s" % (e)})
        self._cr.commit()



    def hubspot_to_odoo_import_contacts(self, hubspot_crm = False):
        hubspot_operation = hubspot_crm.create_hubspot_operation('customer','import',hubspot_crm,'Procesando...')
        self._cr.commit()
        try:
            after = 0
            while True:

                payload = {
                    "filterGroups":[{
                        "filters":[
                            {"propertyName": "firstname", "operator": "HAS_PROPERTY"},
                            {"propertyName": "email", "operator": "HAS_PROPERTY"},
                        ]
                    }],
                    "sorts":[
                        {"direction": "ASCENDING", "propertyName":"hs_object_id"}
                    ],
                    "properties":["hs_object_id,firstname,lastname,email,zip,address,phone,mobilephone,website,country,city,state,hubspot_owner_id,company"],
                    "limit":50,
                    "after":after
                }
                response_status, response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("POST","objects/contacts/search",{}, payload)

                if response_status:
                    for contact in response_data.get('results', []):
                        contact_info = self.env['res.partner'].search([('hubspot_contact_id','=',contact.get('id')),('is_company','=',False)], limit=1)
                        if not contact_info:
                            contact_info = self.env['res.partner'].search([('is_company','=',False),('email','=',contact.get('properties').get('email'))], limit=1)

                        # country = contact.get('properties').get('country',False) if contact.get('properties').get('country') is not None else False
                        # country_id = self.env['res.country'].search([('name', 'like', country[0])], limit=1) if country else False

                        # state = contact.get('properties').get('state',False) if contact.get('properties').get('state') is not None else False
                        # state_id = self.env['res.country.state'].search([('code', 'like', state[0])], limit=1) if state else False

                        user_id = contact.get('properties').get('hubspot_owner_id',False)
                        if user_id and user_id != '':
                            user_id = self.env['res.users'].get_user_data_from_hubspot(hubspot_crm, user_id, hubspot_operation)
                        else:
                            user_id = False

                        fecha_modificacion = contact.get('properties').get('lastmodifieddate')
                        fecha_modificacion = hubspot_crm.convert_date_iso_format(fecha_modificacion)

                        company_id = False
                        assoc_status, assoc_res = hubspot_crm.send_get_request_from_odoo_to_hubspot("GET",("objects/contacts/%s/associations/companies" % contact.get('id')))
                        if assoc_status:
                            try:
                                company_id = assoc_res.get('results')[0].get('id')
                                company_id = self.env['res.partner'].search([('hubspot_contact_id','=',company_id)])
                                if company_id:
                                    company_id = company_id.id
                            except Exception as e:
                                pass
                        
                        name = contact.get('properties').get('firstname','') if contact.get('properties').get('firstname','') is not None else ''
                        name = name + ' ' + contact.get('properties').get('lastname','') if contact.get('properties').get('lastname','') is not None else ''

                        if not contact_info:
                            #creamos el contacto
                            contact_info = super(ResPartner_HubSpot, self).create({
                                'name': name,
                                'email': contact.get('properties').get('email',False),
                                'phone': contact.get('properties').get('phone',False),
                                'mobile': contact.get('properties').get('mobilephone',False),
                                'website': contact.get('properties').get('website',False),
                                'street': contact.get('properties').get('address',False),
                                'city': contact.get('properties').get('city',False),
                                # 'country_id': country_id.id if country_id else False,
                                # 'state_id': state_id.id if state_id else False,
                                'zip': contact.get('properties').get('zip',False),
                                'user_id': user_id.id if user_id else False,
                                'parent_id': company_id,
                                'is_company': False,
                                'hubspot_contact_id': contact.get('properties').get('hs_object_id'),
                                'hubspot_contact_imported': True,
                                'hubspot_crm_id': hubspot_crm.id,
                                'hubspot_write_date': fecha_modificacion,
                            })
                            process_message = "Contacto Creada: {0}".format(contact_info.name)
                        else:
                            if (contact_info.hubspot_write_date and fecha_modificacion > contact_info.hubspot_write_date):
                                # editamos el contacto
                                super(ResPartner_HubSpot, contact_info).write({
                                    'name': name,
                                    'email': contact.get('properties').get('email',False),
                                    'phone': contact.get('properties').get('phone',False),
                                    'mobile': contact.get('properties').get('mobilephone',False),
                                    'website': contact.get('properties').get('website',False),
                                    'street': contact.get('properties').get('address',False),
                                    'city': contact.get('properties').get('city',False),
                                    # 'country_id': country_id.id if country_id else False,
                                    # 'state_id': state_id.id if state_id else False,
                                    'zip': contact.get('properties').get('zip',False),
                                    'user_id': user_id.id if user_id else False,
                                    'is_company': False,
                                    'hubspot_contact_id': contact.get('properties').get('hs_object_id'),
                                    'hubspot_contact_imported': True,
                                    'hubspot_crm_id': hubspot_crm.id,
                                    'hubspot_write_date': fecha_modificacion,
                                })
                                process_message = "Contacto Actualizada: {0}".format(contact_info.name)
                            else:
                                process_message = "Contacto no actualizado por fecha de modificación: {0}".format(contact_info.name)

                        hubspot_crm.create_hubspot_operation_detail('customer', 'import', False, response_data, hubspot_operation, False, process_message)
                        self._cr.commit()

                    if response_data.get('paging', False) and response_data.get('paging').get('next',False) and response_data.get('paging').get('next').get('after',False):
                        after = response_data.get('paging').get('next').get('after')
                    else:
                        break

                else:
                    process_message = "Error en la respuesta de importación de Contacto {}".format(response_data)
                    hubspot_crm.create_hubspot_operation_detail('customer','import','',response_data,hubspot_operation,True,process_message)
                    break

        except Exception as e:
            process_message="Error en la respuesta de importación de contacto {}".format(e)
            _logger.info(process_message)
            hubspot_crm.create_hubspot_operation_detail('customer','import',response_data,process_message,hubspot_operation,True,process_message)
            hubspot_operation.write({'hubspot_message': "El proceso aún no está completo, ocurrio un Error! %s" % (e)})
        self._cr.commit()
    
    def hubspot_to_odoo_export_contacts(self, hubspot_crm):
        hubspot_operation = hubspot_crm.create_hubspot_operation('customer','export',hubspot_crm,'Procesando...')
        self._cr.commit()
        try:
            contacts = self.env['res.partner'].search([('hubspot_contact_id','=',False),('active','=',True),('is_company','=',False)])
            if contacts:
                for contact in contacts:
                    payload = {
                        "properties":{
                            "firstname": contact.name,
                            "lastname": "",
                            "email": contact.email or "",
                            "phone": contact.phone or "",
                            "website": contact.website or "",
                            "company": contact.company_name or ""
                        }
                    }
                    response_status, response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("POST","objects/contacts",{}, payload)
                    if response_status:
                        fecha_modificacion = response_data.get('properties').get('lastmodifieddate')
                        fecha_modificacion = hubspot_crm.convert_date_iso_format(fecha_modificacion)

                        super(ResPartner_HubSpot, contact).write({
                            'hubspot_contact_id': response_data.get('id'),
                            'hubspot_crm_id': hubspot_crm.id,
                            'hubspot_write_date': fecha_modificacion,
                        })
                        process_message = "Contacto creado en hubspot: {}".format(contact.name)
                    else:
                        process_message="Error en la exportación del contacto {}".format(contact.name)
                        hubspot_crm.create_hubspot_operation_detail('customer','export',response_data,process_message,hubspot_operation,True,process_message)
                        hubspot_operation.write({'hubspot_message': "El proceso aún no está completo, ocurrio un Error! %s" % (process_message)})
                hubspot_crm.create_hubspot_operation_detail('customer', 'export', False, response_data, hubspot_operation, False, process_message)
                self._cr.commit()
        except Exception as e:
            process_message="Error en la respuesta de importación de contacto {}".format(e)
            _logger.info(process_message)
            hubspot_crm.create_hubspot_operation_detail('customer','import',response_data,process_message,hubspot_operation,True,process_message)
            hubspot_operation.write({'hubspot_message': "El proceso aún no está completo, ocurrio un Error! %s" % (e)})
        self._cr.commit()

    

    # def get_company_data_from_hubspot(self, hubspot_crm, hubspot_company_id):
    #     hubspot_operation = hubspot_crm.create_hubspot_operation('contact_company','import',hubspot_crm,'Procesando...')
    #     self._cr.commit()
    #     try:
    #         response_status, response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("GET",("objects/companies/%s" % hubspot_company_id))
    #         if response_status:
                
    #             contact_company = self.env['res.partner'].search([('hubspot_contact_id', '=', response_data.get('id')),('is_company','=',True)], limit=1)
    #             if not contact_company:
    #                 contact_company = self.env['res.partner'].create({
    #                     'name': response_data.get('properties').get('name'),
    #                     'company_type': 'company',
    #                     'hubspot_contact_id': response_data.get('properties').get('hs_object_id'),
    #                     'hubspot_contact_imported': True,
    #                     'hubspot_crm_id': hubspot_crm.id
    #                 })
    #                 process_message = "Contacto Empresa Creada: {0}".format(contact_company.name)
    #             else:
    #                 contact_company.write({
    #                     'name': response_data.get('properties').get('name'),
    #                     'hubspot_contact_id': response_data.get('properties').get('hs_object_id'),
    #                     'company_type': 'company',
    #                 })
    #                 process_message = "Contacto Empresa Actualizada: {0}".format(contact_company.name)
                    
    #             hubspot_crm.create_hubspot_operation_detail('contact_company', 'import', False, response_data, hubspot_operation, False, process_message)
    #             self._cr.commit()
    #         else:
    #             process_message = "Error en la respuesta de importación de contacto Empresa {}".format(response_data)
    #             hubspot_crm.create_hubspot_operation_detail('contact_company','import','',response_data,hubspot_operation,True,process_message)
            
    #         hubspot_operation.write({'hubspot_message': "¡El proceso de importar contacto empresa se completó con éxito!"})
    #     except Exception as e:
    #         process_message="Error en la respuesta de importación de contacto empresa {}".format(e)
    #         _logger.info(process_message)
    #         hubspot_crm.create_hubspot_operation_detail('contact_company','import',response_data,process_message,hubspot_operation,True,process_message)
    #         hubspot_operation.write({'hubspot_message': "El proceso aún no está completo, ocurrio un Error! %s" % (e)})
    #     self._cr.commit()
    #     return contact_company

    # def get_contact_data_from_hubspot(self, hubspot_crm, hubspot_contact_id):
        
    #     hubspot_operation = hubspot_crm.create_hubspot_operation('customer','import',hubspot_crm,'Procesando...')
    #     self._cr.commit()
    #     try:
    #         response_status, response_data = hubspot_crm.send_get_request_from_odoo_to_hubspot("GET",("objects/contacts/%s" % hubspot_contact_id))
    #         if response_status:
                
    #             contact_company = self.env['res.partner'].search([('hubspot_contact_id', '=', response_data.get('id')),('is_company','=',False),('email', '=', response_data.get('properties').get('email'))], limit=1)
    #             if not contact_company:
    #                 contact_company = self.env['res.partner'].create({
    #                     'name': response_data.get('properties').get('firstname','') + " " + response_data.get('properties').get('lastname',''),
    #                     'email': response_data.get('properties').get('email',False),
    #                     'phone': response_data.get('properties').get('phone',False),
    #                     'website': response_data.get('properties').get('website',False),
    #                     'street': response_data.get('properties').get('address',False),
    #                     #'state_id': response_data.get('properties').get('state',False),
    #                     'zip': response_data.get('properties').get('zip',False),
    #                     'company_type': 'person',
    #                     'hubspot_contact_id': response_data.get('properties').get('hs_object_id'),
    #                     'hubspot_contact_imported': True,
    #                     'hubspot_crm_id': hubspot_crm.id
    #                 })
    #                 process_message = "Contacto Creada: {0}".format(contact_company.name)
    #             else:
    #                 contact_company.write({
    #                     'name': response_data.get('properties').get('firstname','') + " " + response_data.get('properties').get('lastname',''),
    #                     'email': response_data.get('properties').get('email',False),
    #                     'phone': response_data.get('properties').get('phone',False),
    #                     'website': response_data.get('properties').get('website',False),
    #                     #'state_id': response_data.get('properties').get('state',False),
    #                     'street': response_data.get('properties').get('address',False),
    #                     'zip': response_data.get('properties').get('zip',False),
    #                     'company_type': 'person',
    #                     'hubspot_contact_id': response_data.get('properties').get('hs_object_id'),
    #                 })
    #                 process_message = "Contacto Actualizada: {0}".format(contact_company.name)
                    
    #             hubspot_crm.create_hubspot_operation_detail('customer', 'import', False, response_data, hubspot_operation, False, process_message)
    #             self._cr.commit()
    #         else:
    #             process_message = "Error en la respuesta de importación de contacto {}".format(response_data)
    #             hubspot_crm.create_hubspot_operation_detail('customer','import','',response_data,hubspot_operation,True,process_message)
            
    #         hubspot_operation.write({'hubspot_message': "¡El proceso de importar contacto se completó con éxito!"})
    #     except Exception as e:
    #         process_message="Error en la respuesta de importación de contacto {}".format(e)
    #         _logger.info(process_message)
    #         hubspot_crm.create_hubspot_operation_detail('customer','import',response_data,process_message,hubspot_operation,True,process_message)
    #         hubspot_operation.write({'hubspot_message': "El proceso aún no está completo, ocurrio un Error! %s" % (e)})
    #     self._cr.commit()
    #     return contact_company