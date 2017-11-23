# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Qdoo Order Import',
    'version' : '10.0.1.0',
    'summary': '采购订单销售订单导入',
    'sequence': 30,
    'description': """
采购订单导入,销售订单导入
    """,
    'category': 'sale',
    'website': 'www.qdodoo.com',
    'depends' : ['sale','purchase'],
    'data': [
        #'security/account_security.xml',
        #'security/ir.model.access.csv',
        'purchase_import.xml',
        'sale_import.xml',
    ],
    'installable':True,
}
