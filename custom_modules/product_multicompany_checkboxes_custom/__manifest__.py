# -*- coding: utf-8 -*-
{
    'name': "Product Multicompany Checkbox Custom",

    'summary': """
        This module enables a checkbox to select multi companies in a product.""",

    'description': """
        Module to add a checkbox to select multi companies.
    """,

    'author': "Develoop",
    'website': "https://www.develoop.net",
    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['base_multi_company', 'product_multi_company', 'sale_stock', 'sale'],

    'data': [
        'views/product_template_custom.xml',
    ],
    "images": ['static/description/icon.png'],
    "installable": True,
    "application": True,
    "auto_install": False,
}
