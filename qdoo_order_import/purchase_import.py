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


class PurchaseOrder(models.Model):
    """
        采购明细导入
    """
    _inherit = 'purchase.order'    # 继承

    import_file = fields.Binary(string="导入的模板")

    @api.one
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
            purchase_line_obj = self.env['purchase.order.line']
            product_pricelist = self.env['product.pricelist']
            lst = []
            for obj in range(1, product_info.nrows):
                val = {}
                # 获取产品编号
                default_code = product_info.cell(obj, 0).value
                if not default_code:
                    raise UserError(u'第%s行，产品编号不能为空'%obj)
                # 获取计划日期
                if product_info.cell(obj, 3).value:
                    plan_date = datetime.strptime(product_info.cell(obj, 3).value, '%Y-%m-%d')
                else:
                    plan_date = datetime.now().date()
                # 获取产品数量
                product_qty = product_info.cell(obj, 4).value
                if not product_qty:
                    raise UserError(u'第%s行，产品数量不能为空'%obj)
                # 获取公司id
                company_name = product_info.cell(obj, 2).value
                if not company_name:
                    raise UserError(u'第%s行，公司不能为空'%obj)
                company = company_obj.search([('name','=',company_name)])
                if not company:
                    raise UserError(u'未在系统中查询到%s公司'%company_name)
                # 查询系统中对应的产品id
                product = product_obj.search([('default_code', '=', default_code), ('company_id', '=', company.id)])
                if not product:
                    raise UserError(u'本公司没有编号为%s的产品'% default_code)

                seller = product._select_seller(
                    partner_id=self.partner_id,
                    quantity=product_qty,
                    date=self.date_order and self.date_order[:10],
                    uom_id=product.uom_id)

                #price_unit = self.env['account.tax']._fix_tax_included_price(seller.price, product.supplier_taxes_id, self.taxes_id) if seller else 0.0
                price_unit = seller.price if seller else 0.0
                if price_unit and seller and wiz.currency_id and seller.currency_id != wiz.currency_id:
                    price_unit = seller.currency_id.compute(price_unit, wiz.currency_id)

                if seller and product.uom_id and seller.product_uom != product.uom_id:
                    price_unit = seller.product_uom._compute_price(price_unit, product.uom_id)
                if not seller:
                    price_unit = product.standard_price
                val['product_id'] = product.id
                val['name'] = product.name
                val['date_planned'] = plan_date
                val['company_id'] = product.company_id.id
                val['product_qty'] = product_qty
                val['product_uom'] = product.uom_id.id
                val['price_unit'] = product_info.cell(obj, 5).value if product_info.cell(obj, 5).value else price_unit
                val['order_id'] = wiz.id
                lst.append(val)
            for res in lst:
                purchase_line_obj.create(res)
            wiz.import_file = ''
        else:
            raise UserError(u'请先上传模板')

