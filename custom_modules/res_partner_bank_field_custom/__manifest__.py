# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name" : 'Account Bank Field Custom',
    "summary": "Custom Bank Value on bank account.",
    "version": "13.0.0.0.0",
    "category": "",
    "description": "Nuevo campo personalizado en cuenta bancaria.",
    "author": "Develoop Software",
    "website": "https://www.develoop.net",
    'depends': ['base', 'sale'],
    'data': [
        'views/res_partner_invoice_value_view.xml'
    ],
    "images": ['static/description/icon.png'],
    'auto_install': False,
    'installable': True,
}
