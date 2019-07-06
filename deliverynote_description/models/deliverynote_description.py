# -*- coding: utf-8 -*-

from odoo import fields, models, api


class deliverydesc(models.Model):
    _inherit = "stock.pack.operation"


    desc=fields.Char("Description")


