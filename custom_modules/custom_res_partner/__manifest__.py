{
    'name': 'Nsing Partner custom',
    'version': '13.0.1.0',
    'summary': """Campos personalizados.""",
    'description': """
        Modulo de personalizacion del modulo partner, campo pedido de compra.
    """,
    'depends': ['base', 'account', 'sale', 'web'],
    'data': [
        'views/res_partner_view.xml',
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
