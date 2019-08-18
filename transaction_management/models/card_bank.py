# -*- coding: utf-8 -*-

from odoo import fields, models


class CardBank(models.Model):
    _name = "card.bank"

    name = fields.Char(string='Bank', required=True)
    _sql_constraints = [('name_uniq', 'unique (name)', 'The name of the bank must be unique !')]
