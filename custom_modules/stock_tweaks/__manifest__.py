# -*- coding: utf-8 -*-
{
    'name': 'Agregados Inventarios',
    'version': '1.1',
    'summary': 'Modificaciones comportamiento de inventarios',
    'description': """
    Fecha efectiva de albarán editable y sincronizada con movimientos generados. 
    """,
    'author': 'DEVELOOP',
    'category': 'stock',
    'website': 'https://www.develoop.net',
    'depends': ['base', 'stock'],
    'data': [
        'views/stock_picking_views.xml',
        'reports/report_value_picking.xml'
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
