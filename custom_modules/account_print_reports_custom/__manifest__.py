{
    'name': 'Account Print Reports custom',
    'version': '0.0',
    'summary': """Modificacion del dominio.""",
    'description': """
        Modulo personalizado de modificacion de reportes impresos de facturas, compras y ventas.
    """,
    'depends': ['base','account', 'sale', 'purchase','res_partner_bank_field_custom'],
    'data': [
        'views/invoice_custom.xml',
        'views/sale_order_custom.xml',
        'views/purchase_order_custom.xml',
        'views/external_layout_box_custom.xml'
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
