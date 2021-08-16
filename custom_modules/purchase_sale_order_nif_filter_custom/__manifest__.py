# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name" : 'Purchase Sale Order NIF Filter Odoo Custom',
    "summary": "Purchase Sale Order NIF Filter.",
    "version": "13.0.0.0.0",
    "category": "",
    "description": "Filtro personalizado de busqueda de pedido de venta y pedido de compra por NIF(VAT) y Nombre de cliente.",
    "author": "Develoop Software",
    "website": "https://www.develoop.net",
    'depends': ['base', 'sale', 'purchase', 'account'],
    'data': [
        'views/sale_order_nif_filter_view.xml',
        'views/purchase_order_nif_filter_view.xml',
        'views/contact_nif_filter_view.xml'
    ],
    "images": ['static/description/icon.png'],
    'auto_install': False,
    'installable': True,
}
