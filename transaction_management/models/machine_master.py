# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class MachineMaster(models.Model):
    _inherit = ["multi.company.abstract"]
    _name = "machine.master"
    _description = "Machine Master"

    bname = fields.Many2one('company.branch', string ="Branch")
    name = fields.Char(string='Machine Name')
    merchant_id = fields.Char(string='Merchant ID',)
    terminal_id = fields.Char(string='Terminal ID', )
    bank_name = fields.Many2one('machine.bank', string='Bank Name', ondelete='restrict')
    rented =fields.Boolean(string='is Machine Rented')
    rented_from = fields.Many2one('res.partner', string="Rented From", ondelete='restrict')
    sales_percentage = fields.Float(string='Default Sales Percentage')
    cost_percentage = fields.Float(string='Cost Percentage')
    merchant_bank_ac = fields.Many2one('account.account', string="Bank Account", ondelete='restrict',
                                       domain=lambda self: [('user_type_id', '=', self.env.ref('account.data_account_type_liquidity').id),])
    cost_ac = fields.Many2one('account.account', string="Cost Account",required=True, ondelete='restrict')
    income_ac = fields.Many2one('account.account', string="Income Account",required=True, ondelete='restrict')
    cash_ac = fields.Many2one('account.account', string="Cash Account",required=True, ondelete='restrict')

    @api.onchange('bname')
    def _onchange_bname(self):
        self.cost_ac = self.bname.cost_ac.id
        self.income_ac = self.bname.income_ac.id
        self.cash_ac = self.bname.cash_ac.id