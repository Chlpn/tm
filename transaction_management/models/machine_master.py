# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class MachineMaster(models.Model):
    _name = "machine.master"
    _description = "Machine Master"

    name = fields.Char(string='Machine Name')
    merchant_id = fields.Char(string='Merchant ID',)
    terminal_id = fields.Char(string='Terminal ID', )
    bank_name = fields.Many2one('customer.bank', string='Bank Name')
    rented =fields.Boolean(string='is Machine Rented')
    rented_from = fields.Many2one('res.partner', string="Rented From")
    sales_percentage = fields.Float(string='Default Sales Percentage')
    cost_percentage = fields.Float(string='Cost Percentage')
    merchant_bank_ac = fields.Many2one('account.account', string="Bank Account",)
                    #domain=lambda self: [('user_type_id', '=', self.env.ref('data_account_type_liquidity').id)])
    cost_ac = fields.Many2one('account.account', string="Cost Account",required=True,)
                    #domain=lambda self: [('user_type_id', '=', self.env.ref('data_account_type_direct_costs').id)])
    income_ac = fields.Many2one('account.account', string="Income Account",required=True,)
                    #domain=lambda self: [('user_type_id', '=', self.env.ref('data_account_type_revenue').id)])
    cash_ac = fields.Many2one('account.account', string="Cash Account",required=True,)
                    #domain=lambda self: [('user_type_id', '=', self.env.ref('data_account_type_liquidity').id)])

