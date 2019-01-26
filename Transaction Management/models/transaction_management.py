# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class TransMaster(models.Model):
    _name = "trans.master"
    _description = "Transaction Management"
    _rec_name = 'transaction_no'

    transaction_no = fields.Char(string='Transaction Number', readonly=True, store=True)
    transaction_date = fields.Date(string='Date',default=fields.Date.context_today, required=True)
    commission_included = fields.Boolean(string='is commission included')
    amount_to_swipe = fields.Float(string='Amount to Swipe')
    amount_to_customer = fields.Float(string='Amount to customer')
    commission = fields.Float(string='Commission')
    cost_to_commission = fields.Float(string='Cost of Commission', readonly=True, store=True)
    margin = fields.Float(string='margin', readonly=True, store=True)
    cash_paid_customer = fields.Float(string='Cash Paid')
    balance = fields.Float(string='Balance', readonly=True, store=True)
    machine_name = fields.Many2one('machine.master')
    sales_percentage = fields.Float(string='Sales Percentage')
    cost_percentage = fields.Float(string='Cost Percentage', readonly=True, store=True)
    customer = fields.Many2one('res.partner', string="Customer")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft',readonly=True)

    @api.onchange('machine_name')
    def _onchange_machine_name(self):
        self.sales_percentage = self.machine_name.sales_percentage
        self.cost_percentage =self.machine_name.cost_percentage



    @api.onchange('amount_to_customer','amount_to_swipe','sales_percentage')
    def _onchange_amount_to_customer(self):
        if not self.machine_name:
            raise UserError(_('Please select the Machine Name'))
        else:

            if self.commission_included == False:
                self.amount_to_swipe = (self.amount_to_customer * 100/(100-self.sales_percentage))
                self.commission = self.amount_to_swipe - self.amount_to_customer
                self.cost_to_commission = (self.amount_to_swipe * self.cost_percentage / 100)
                self.cash_paid_customer = self.amount_to_customer
                self.balance = self.amount_to_customer - self.cash_paid_customer
                self.margin = self.commission - self.cost_to_commission
            else:
                self.commission = (self.amount_to_swipe * self.sales_percentage / 100)
                self.amount_to_customer = (self.amount_to_swipe - self.commission)
                self.cost_to_commission = (self.amount_to_swipe * self.cost_percentage / 100)
                self.cash_paid_customer = self.amount_to_customer
                self.balance = self.amount_to_customer - self.cash_paid_customer
                self.margin = self.commission - self.cost_to_commission

    @api.multi
    def save(self):
        self.transaction_no = self.env['ir.sequence'].next_by_code('trans.master') or 'new'