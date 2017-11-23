# -*- coding: utf-8 -*-

{
    'name': "Tea Community Theme",
    'author': "RStudio",
    'website': "",
    'sequence': 1,
    'installable': True,
    'application': True,
    'auto_install': False,
    'summary': u"""
        Backend/AppSwither/Sidebar/Switch Theme.
        """,
    'description': u"""

    """,
    "category": "Themes/Backend",
    'version': '10.0.1.4',
    'depends': [
        'web',
    ],
    'data': [
        'views/assets.xml',
        'views/backend.xml',
        'views/setting_views.xml',
        'views/login_template.xml',
        'views/login_views.xml',
    ],
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'live_test_url': 'http://119.29.60.38:8069/web?db=tea',
    'images': ['images/main_screenshot.png'],
    'currency': 'EUR',
    'price': 119,
}
