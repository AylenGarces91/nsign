{
    'name': 'Nuevos fields Custom',
    'category': 'Product',
    'version': '0.0',
    'summary': """Realiza la creacion de nuevos campos en diferentes modulos.""",
    'description': """""",
    'depends': ['base','account'],
    'data': [
        'views/res_partner.xml',
        'views/account_move.xml',
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
