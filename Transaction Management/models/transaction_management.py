# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class TransMaster(models.Model):
    _name = "trans.master"
    _description = "Transaction Management"

    transaction_no = fields.Char(string='Transaction Number', readonly=True)
    transaction_date = fields.Date(string='Date')
    commission_included = fields.Boolean(string='is commission included')
    amount_to_swipe = fields.Float(string='Amount to Swipe')
    amount_to_customer = fields.Float(string='Amount to customer')
    commission = fields.Float(string='Commission')
    cost_to_commission = fields.Float(string='Cost of Commission', readonly=True)
    margin = fields.Float(string='margin', readonly=True)
    cash_paid_customer = fields.Float(string='Cash Paid')
    balance = fields.Float(string='Balance', readonly=True)
    machine_name = fields.Many2one('machine.master')
    sales_percentage = fields.Float(string='Sales Percentage')
    cost_percentage = fields.Float(string='Cost Percentage', readonly=True)
    merchant_bank_ac = fields.Many2one('account.account', string="Partner Account")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled'),
    ], string='Status', readonly=True)

    @api.onchange('machine_name')
    def _onchange_machine_name(self):
        self.sales_percentage = self.machine_name.sales_percentage
        self.cost_percentage =self.machine_name.cost_percentage