# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import amount_to_text_en



class CapitalDrawing(models.Model):
    _inherit = ["multi.company.abstract"]
    _name = "capital.drawing"

    name = fields.Char(string='Name', size=64, readonly=True)
    calculation_date = fields.Date(string='Transaction Date', required=True, default=fields.Date.context_today)
    previous_balance= fields.Float('Previous Balance' , readonly=True)
    gross_profit = fields.Float('Gross Profit' , readonly=True)
    expenses = fields.Float('Total Expenses', readonly=True)
    net_profit = fields.Float('Net Profit', readonly=True)
    lock_amount = fields.Float('received lock amount', readonly=True)
    gross_amount = fields.Float('Amount to Pay', readonly=True)
    amount_paid = fields.Float('Amount Paid', readonly=True)
    amount_received = fields.Float('Amount Received', readonly=True)
    net_amount = fields.Float('Net Balance', readonly=True)
    payment_ref = fields.Many2one('account.move', string="Payment_ref", readonly=True)
    receipt_ref = fields.Many2one('account.move', string="Receipt_ref", readonly=True)
    state = fields.Selection([
        ('dr', 'Draft'),
        ('cal', 'Calculated'),
        ('pd', 'Profit Paid'),
        ('rec', 'Profit Paid & Expense Received'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='dr', readonly=True)
    _sql_constraints = [('name_uniq', 'unique (name)', 'Document Number must be unique !')]
    _defaults = {'name': lambda self, cr, uid, context: 'Capital Drawing'}

