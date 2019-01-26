# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class MachineMaster(models.Model):
    _name = "machine.master"
    _description = "Machine Master"

    name = fields.Char(string='Machine Name')
    merchant_id = fields.Char(string='Merchant ID',)
    terminal_id = fields.Char(string='Terminal ID', )
    bank_name = fields.Many2one('customer.bank', string='Bank Name', readonly=True)
    date_issue = fields.Date(string='Printed On', readonly=True)