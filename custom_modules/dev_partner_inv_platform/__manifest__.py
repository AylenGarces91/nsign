# -*- coding: utf-8 -*-
{
    'name': 'Plataforma de facturas Cliente',
    'version': '1.0',
    'summary': 'Especificar envío de facturas',
    'description': """
    Agrega un campo para especificar la plataforma destino de las facturas correspondientes al cliente.

    Las facturas Odoo obtienen una bandera que indica si fueron enviadas por medio de la plataforma especificada en ficha de cliente.
    """,
    'author': 'DEVELOOP',
    'category': 'account',
    'website': 'https://www.develoop.net',
    'depends': ['base', 'account'],
    'data': [
        'views/res_partner_views.xml',
        'views/account_move_views.xml'
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
