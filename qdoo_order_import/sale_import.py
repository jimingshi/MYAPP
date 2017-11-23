# -*- coding: utf-8 -*-
###########################################################################################
#
#    module name for OpenERP
#    Copyright (C) 2015 qdodoo Technology CO.,LTD. (<http://www.qdodoo.com/>).
#
###########################################################################################

from odoo import fields, models, api, _
import xlrd,base64
from datetime import timedelta, datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    """
        销售明细导入
    """
    _inherit = 'sale.order'    # 继承

    import_file = fields.Binary(string="导入的模板")

    def import_data(self):
        wiz = self
        if wiz.import_file:
            try:
                excel = xlrd.open_workbook(file_contents=base64.decodestring(wiz.import_file))
            except:
                raise UserError(u'请使用xls文件进行上传')
            product_info = excel.sheet_by_index(0)
            product_obj = self.env['product.product']
            company_obj = self.env['res.company']
            sale_line_obj = self.env['sale.order.line']
            product_pricelist = self.env['product.pricelist']
            lst = []
            for obj in range(1, product_info.nrows):
                val = {}
                # 获取产品编号
                default_code = product_info.cell(obj, 0).value
                if not default_code:
                    raise UserError(u'第%s行，产品编号不能为空'%obj)
                # 获取产品数量
                product_qty = product_info.cell(obj, 3).value
                if not product_qty:
                    raise UserError(u'第%s行，产品数量不能为空'%obj)
                # 获取公司id
                company_name = product_info.cell(obj, 2).value
                if not company_name:
                    raise UserError(u'提示'), _(u'第%s行，公司不能为空'%obj)
                company = company_obj.search([('name','=',company_name)])
                if not company:
                    raise UserError(u'未在系统中查询到%s公司' % company_name)
                # 查询系统中对应的产品id
                product = product_obj.search([('default_code', '=', default_code), \
                                                 ('company_id', '=', company.id)])
                if not product:
                    raise UserError(u'%s公司没有编号为%s的产品' % (company_name,default_code))


                # pricelist_id = wiz.pricelist_id.id
                # if pricelist_id:
                #     date_order_str = datetime.strptime(wiz.date_order, DEFAULT_SERVER_DATETIME_FORMAT).strftime(DEFAULT_SERVER_DATE_FORMAT)
                #     price = product_pricelist.price_get(cr, uid, [pricelist_id],
                #             product.id, product_qty, wiz.partner_id or False, {'uom': product.uom_id.id, 'date': date_order_str})[pricelist_id]
                # else:
                #     price = product.standard_price

                if wiz.pricelist_id and wiz.partner_id:
                    price_unit = product.with_context(pricelist=self.pricelist_id.id).price
                else:
                    price_unit = product.lst_price
                val['product_id'] = product.id
                val['name'] = product.name
                val['company_id'] = product.company_id.id
                val['product_uom_qty'] = product_qty
                val['product_uom'] = product.uom_id.id
                val['price_unit'] = product_info.cell(obj, 4).value if product_info.cell(obj, 4).value else price_unit
                val['order_id'] = wiz.id
                lst.append(val)
            for res in lst:
                sale_line_obj.create(res)
            self.import_file = ''
        else:
            raise UserError(u'请先上传模板')

