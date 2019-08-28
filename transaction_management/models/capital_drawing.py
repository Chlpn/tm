# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import amount_to_text_en



class CapitalDrawing(models.Model):
    _inherit = ["multi.company.abstract"]
    _name = "capital.drawing"

    name = fields.Char(string='Name', size=64, readonly=True)
    calculation_date = fields.Date(string='Transaction Date', required=True, default=fields.Date.context_today)
    previous_balance= fields.Float('Previous Balance' )
    gross_profit = fields.Float('Gross Profit' )
    expenses = fields.Float('Total Expenses')
    net_profit = fields.Float('Net Profit')
    lock_amount = fields.Float('received lock amount')
    gross_amount = fields.Float('Amount to Pay')
    amount_paid = fields.Float('Amount Paid')
    amount_received = fields.Float('Amount Received')
    net_amount = fields.Float('Net Balance')
    payment_ref = fields.Many2one('account.move', string="Payment_ref")
    receipt_ref = fields.Many2one('account.move', string="Receipt_ref")
    state = fields.Selection([
        ('dr', 'Draft'),
        ('cal', 'Calculated'),
        ('pd', 'Profit Paid'),
        ('rec', 'Profit Paid & Expense Received'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='dr', readonly=True)
    _sql_constraints = [('name_uniq', 'unique (name)', 'Document Number must be unique !')]
    _defaults = {'name': lambda self, cr, uid, context: 'Capital Drawing'}
