# -*- coding: utf-8 -*-
{
    'name': "Product Pack Extras",
    'version': '0.1',
    'author': "Develoop Software",
    'category': 'Uncategorized',
    'summary': 'Especificaciones para kits de productos',
    'website': "https://www.develoop.net/",
    'description': """
        Reparticion ponderada de precios de componentes de kits de productos.
        """,
    'depends': ['sale','product_pack'],
    'data': [
        'views/product_pack_line_views.xml',
    ],
    'demo': [],
    'installable': True,
}