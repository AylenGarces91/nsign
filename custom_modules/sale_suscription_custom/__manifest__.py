{
    'name': 'Venta y suscripcion custom',
    'category': 'Product',
    'version': '0.0',
    'summary': """Modificacion del dominio.""",
    'description': """""",
    'depends': ['base','sale','sale_subscription'],
    'data': [
        'views/sale_order.xml',
        'views/sale_subscription.xml',
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
