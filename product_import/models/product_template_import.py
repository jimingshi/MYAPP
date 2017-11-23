# -*- coding: utf-8 -*-
import base64
import xlrd
import re
from odoo import models,fields,api,_
from odoo.exceptions import UserError


class product_import(models.Model):
    _name = 'product.template.import'
    _description = u'产品模板导入'

    excel = fields.Binary(u'文件', attachment=True, required=True)

    @api.multi
    def btn_import(self):
        import sys
        reload(sys)
        sys.setdefaultencoding('utf8')

        try:
            wb = xlrd.open_workbook(file_contents=base64.decodestring(self.excel))
        except:
            raise UserError(_('文件格式不匹配或文件内容错误.'))

        self._cr.execute("select name,id from res_partner where supplier = 't'")
        gys_dict = dict(self._cr.fetchall())

        self._cr.execute("select name,id from product_uom where active = 'TRUE'")
        uom_dict = dict(self._cr.fetchall())

        for sheet in wb.sheets():
            self._handle_mx(sheet, gys_dict,uom_dict)

    def _handle_attribute(self):
        '''
        获取当前数据库中 product.attribute 里属性名及属性值关系
        :return:{
            属性名：{
                id:属性名id,
                vals:{
                    属性值名称1：属性值id1,
                    属性值名称2：属性值id2,
                }
            }
        }
        '''
        res = {}

        self._cr.execute("select name,id from product_attribute;")
        att_dict = {}
        for name, id in self._cr.fetchall():
            res[name] = {'id': id, 'vals': {}}
            att_dict[id] = name

        self._cr.execute("select attribute_id,name,id from product_attribute_value;")
        for att_id, name, id in self._cr.fetchall():
            res[att_dict[att_id]]['vals'][name] = id

        return res

    @api.multi
    def _handle_mx(self, sheet, gys_dict,uom_dict):

        att_dict = self._handle_attribute()

        self._cr.execute("select name from product_template;")
        pt_list = [a for (a,) in self._cr.fetchall()]

        self._cr.execute("select default_code from product_template;")
        code_list = [a for (a,) in self._cr.fetchall()]

        # 直接从第2行开始读取数据
        for i in range(1, sheet.nrows):
            line = i+1
            # 获取产品名称
            product_template_name = sheet.cell(i, 0).value.strip()
            if not product_template_name:
                raise UserError(u'第%s行，产品名称不能为空' % line)

            # 获取内部参考
            code = sheet.cell(i, 1).value

            # 如果内部参考是数值类型，把数值型转换为字符型
            if code != '' :
                if type(code) is type(1.0) or type(code) is type(1):
                    code = str(int(code))

            # 判断内部参考是否为空
            if not code:
                raise UserError(u'第%s行，内部参考不能为空' % i)

            # 防止重复导入,可更换别的条件
            if code in code_list:
                raise UserError(u'第%s行，'% line + u'内部参考"%s"已存在于导入的Excel中或系统中'  %code)

            pt_list.append(product_template_name)
            code_list.append(code)

            # 获取内部类别
            categ = sheet.cell(i, 2).value
            if not categ:
                raise UserError(u'第%s行，内部类别不能为空' % line)

            # 获取计量单位、采购计量单位
            uom_name = sheet.cell(i, 6).value
            if not uom_name:
                raise UserError(u'第%s行，计量单位不能为空' % line)
            uom_po_name = sheet.cell(i, 7).value
            if not uom_po_name:
                raise UserError(u'第%s行，采购计量单位不能为空' % line)
            # 判断计量单位是否存在，不存在新建。新建时，计量单位类型默认是"单位"
            if uom_name:
                if uom_name in uom_dict:
                    uom_id = uom_dict[uom_name]
                else:
                    uom_id = self.env['product.uom'].create({
                        'name': uom_name,
                        'category_id': self.env['product.uom.categ'].search([('name', '=', '单位')]).id,
                    }).id
                    uom_dict[uom_name] = uom_id

            # 判断采购计量单位是否存在，不存在新建。新建时，采购计量单位类型默认是"单位"
            if uom_po_name:
                if uom_po_name in uom_dict:
                    uom_po_id = uom_dict[uom_po_name]
                else:
                    uom_po_id = self.env['product.uom'].create({
                        'name': uom_po_name,
                        'category_id': self.env['product.uom.categ'].search([('name', '=', '单位')]).id,
                    }).id
                    uom_dict[uom_po_name] = uom_po_id


            tracking = sheet.cell(i, 8).value
            product_type = sheet.cell(i, 9).value
            list_price = sheet.cell(i, 10).value



            vals = {
                'name': product_template_name,
                'default_code': code,
                'categ_id': self.env['product.category'].search([('name', '=', categ)]).id,
                'uom_id':uom_id,
                'uom_po_id':uom_po_id,
                'tracking':tracking,
                'list_price':list_price,
                'type':product_type,
            }

            # 如果联系人中没有此供应商，进行添加
            gys_name = sheet.cell(i, 3).value
            gys_product_name = sheet.cell(i, 4).value
            gys_price = sheet.cell(i, 5).value
            if gys_name:
                if gys_name in gys_dict:
                    gys_id = gys_dict[gys_name]
                else:
                    gys_id = self.env['res.partner'].create({
                        'name': gys_name,
                        'company_type': 'company',
                        'supplier': True,
                        'customer': False,
                    }).id
                    gys_dict[gys_name] = gys_id
                vals['seller_ids'] = [[0, 0, {'name': gys_id, 'product_name': gys_product_name,'price': gys_price, }]]

            self.env['product.template'].create(vals)




            for atti_col in range(sheet.ncols-1):
                # 判断属性此列是属性列

                if atti_col<11 or atti_col % 2 == 0 :#属性在偶数列
                # if atti_col<10 or atti_col % 2 == 1 :#属性在偶数列
                # if atti_col<9 or atti_col % 2 == 0 :#属性在奇数列
                    continue
                # 处理变形字段
                att_name = sheet.cell(i, atti_col).value
                att_value_name = sheet.cell(i, atti_col+1).value

                # 如果没有属性跳出
                if not att_name:
                    continue

                vals1 = []
                if att_value_name:
                    # 获取属性
                    if att_name not in att_dict:
                        att_dict[att_name] = {
                            'id': self.env['product.attribute'].create({'name': att_name}).id,
                            'vals': {}
                        }

                    # 获取属性值ids
                    value_ids = []
                    att_values = re.split(u',|，', att_value_name.strip().strip(u',').strip(u'，'))
                    for value in att_values:
                        value = value.strip()
                        if value not in att_dict[att_name]['vals']:
                            att_dict[att_name]['vals'][value] = self.env['product.attribute.value'].create({
                                'name': value,
                                'attribute_id': att_dict[att_name]['id']
                            }).id
                        value_ids.append(att_dict[att_name]['vals'][value])
                        print value_ids

                    vals1.append((0, False, {
                        'attribute_id': att_dict[att_name]['id'],
                        'value_ids': [(6, False, value_ids)]
                    }))


                    self.env['product.template'].search([('name', '=', product_template_name),('default_code', '=', code)]).write({'attribute_line_ids':  vals1})
