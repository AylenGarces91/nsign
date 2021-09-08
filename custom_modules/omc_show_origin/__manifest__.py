# -*- coding: utf-8 -*-
{
    'name': "Show document origin",

    'summary': """
        Show document origin, without method created document 
        """,

    'description': """
        Show description in any case remove property validation
    """,

    'author': "Develoop",
    'website': "https://develoop.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ],
}
