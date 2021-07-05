# -*- coding: utf-8 -*-
{
    'name': "account_reports_custom",
    'summary': """
        Module to extend account reports""",

    'description': """
        This module extends and add more reports based on account report module.
    """,

    'author': "Develoop",
    'website': "https://www.develoop.net/",
    'version': '0.1',
    'depends': ['account_reports'],
    'data': [
        'views/assets.xml',
        'static/src/xml/qweb.xml',
        'data/account_financial_report_data.xml',
    ],
    "images": ['static/description/icon.png'],
    "installable": True,
    "application": True,
    "auto_install": False,
}
