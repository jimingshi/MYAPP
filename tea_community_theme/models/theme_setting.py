# -*- coding: utf-8 -*-

from odoo import models, fields, api



class ThemeSetting(models.Model):
    _name = 'theme_settings'
    _description = 'Theme Setting'

    _inherit = 'res.config.settings'

    login_theme = fields.Selection([('1', 'Login Theme 1'),
                                    ('2', 'Login Theme 2'),
                                    ('3', 'Login Theme 3'),
                                    ('4', 'Login Theme 4'),
                                    ('5', 'Login Theme 5'),
                                    ('6', 'Login Theme 6')],
                                   'Login Theme',  required=True, translate=True)

    sidebar_theme = fields.Selection([('0', 'No Sidebar'),
                                      ('1', 'Narrow'),
                                      ('2', 'Wide')],
                                     'Sidebar Theme', required=True, translate=True)

    enable_footer = fields.Selection([('0', 'disable'),
                                      ('1', 'enable')],
                                     'Enable Footer', required=True, translate=True)

    @api.model
    def get_default_theme(self, fields):
        Param = self.env["ir.config_parameter"]
        return {
            'login_theme': Param.get_param('web.login_theme', default='1'),
            'sidebar_theme': Param.get_param('web.sidebar_theme', default='1'),
            'enable_footer': Param.get_param('web.enable_footer', default='1'),
        }

    @api.multi
    def set_thmeme(self):
        Param = self.env["ir.config_parameter"]
        Param.set_param('web.login_theme', self.login_theme)
        Param.set_param('web.sidebar_theme', self.sidebar_theme)
        Param.set_param('web.enable_footer', self.enable_footer)


PARAMS = [
    ('web.login_theme', '1'),
    ('web.sidebar_theme', '1'),
    ('web.enable_footer', '1'),
]


class IrConfigParameter(models.Model):

    _inherit = 'ir.config_parameter'

    @api.model
    def get_debranding_parameters(self):
        res = {}
        for param, default in PARAMS:
            value = self.env['ir.config_parameter'].get_param(param, default)
            res[param] = value.strip()
        return res

    @api.model
    def create_debranding_parameters(self):
        for param, default in PARAMS:
            if not self.env['ir.config_parameter'].get_param(param):
                self.env['ir.config_parameter'].set_param(param, default or ' ')