# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        order_date = res.date_order
        sequence = res.name
        res.name = 'QTNBN'  + order_date[2:4] + order_date[5:7] + sequence[2:]
        return res