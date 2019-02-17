# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError

class ccPayment(models.Model):
    _name = "cc.payment"
    _description = "Credit Card Payment"
    _rec_name = 'serial'

    company_id = fields.Many2one(
        'res.company',
        'Company',
        default=lambda self: self.env.user.company_id
    )
    serial = fields.Char(string='Ref. No:')
    processing_date = fields.Date(string='Date',default=fields.Date.context_today, required=True)
    payment_amount = fields.Float(string='Payment Amount', digits=dp.get_precision('Account'))
    commission = fields.Float(string='Commission', default=3.0,digits=dp.get_precision('Account'))
    commission_pay = fields.Float(string='Commission to be Paid', digits=dp.get_precision('Account'))
    commission_paid = fields.Float(string='Commission Paid', digits=dp.get_precision('Account'))
    total_to_swipe = fields.Float(string='Amount to Swipe', store=True, digits=dp.get_precision('Account'))
    payment_date = fields.Date(string='Credit Card Payment Date', default=fields.Date.context_today, required=True)
    amount_deposited = fields.Float(string='Amount deposited', store=True, digits=dp.get_precision('Account'))
    amount_to_deposit = fields.Float(string='Amount remaining to deposit', store=True, digits=dp.get_precision('Account'))
    amount_swiped = fields.Float(string='Amount swiped', store=True, digits=dp.get_precision('Account'))


    customer = fields.Many2one('res.partner', string="Customer", ondelete='restrict', domain=[('customer', '=', '1')])
    customer_mobile = fields.Char(related='customer.mobile',string='Mobile')
    payment_ref = fields.Many2one('account.move', string="Payment Reference")
    deposit_ref = fields.Many2one('account.move', string="Deposit Reference")
    transaction_ref = fields.Many2one('account.move', string="Transaction Reference")
    note = fields.Text(string="payment_details")

    state = fields.Selection([
        ('dr', 'Draft'),
        ('up', 'Under Process'),
        ('pd', 'Partially Deposited'),
        ('fd', 'Fully Deposited'),
        ('ps', 'Partially Swiped'),
        ('fs', 'Processed'),
        ('cl', 'Cancelled')
    ], string='Status', default='draft',readonly=True)


    @api.onchange('payment_amount','commission')
    def _onchange_payment_amount(self):
        self.commission_pay = self.payment_amount * self.commission / 100
        self.commission_paid = 0.0
        self.total_to_swipe = self.payment_amount + self.commission_pay
        self.amount_to_deposit = self.total_to_swipe





