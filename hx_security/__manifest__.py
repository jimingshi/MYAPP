# -*- coding: utf-8 -*-
{
    'name': "新华权限模块",

    'summary': """
        新华权限模块""",

    'description': """
        新华权限模块
    """,

    'author': "青岛欧度软件技术有限责任公司",
    'website': "http://www.qdodoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'XH',
    'version': '10.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],
    # 'website_sale','website_version','stock','website_partner','im_livechat'

    # always loaded
    'data': [
        'views/inherit_stock_picking_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
}