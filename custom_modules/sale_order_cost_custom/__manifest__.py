# -*- coding: utf-8 -*-
{
    'name': 'Sale order Custom',
    'category': 'Product',
    'version': '0.0',
    'summary': """Agrega una columna extra 'importe coste' a la vista lista de ventas.""",
    'description': """""",
    'depends': ['base', 'account', 'sale', 'web'],
    'data': [
        'views/sale_order_view.xml',
    ],
    'author': 'Develoop Software',
    'images': ['static/description/icon.png'],
    'maintainer': 'Develoop Software',
    'website': 'https://www.develoop.net',
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False
}
