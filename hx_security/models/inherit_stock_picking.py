# -*- coding: utf-8 -*-
"""
    
Description:
Author:Gala
Versions:
    Created by Gala on 2017/8/9 10:54
"""
import json
from odoo import models, api, fields, _
from odoo.tools import float_is_zero, float_compare

class InheritAccountInvoice(models.Model):

    _inherit = ["stock.picking"]

