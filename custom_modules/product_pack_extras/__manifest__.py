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
    'depends': ['sale','product_pack', 'account', 'account_print_reports_custom'],
    'data': [
        'views/product_pack_line_views.xml',
        'views/saleorder_document_custom.xml',
        'views/account_move_custom.xml',
    ],
    'demo': [],
    'installable': True,
}