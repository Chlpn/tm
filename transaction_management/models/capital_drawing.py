# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import amount_to_text_en
import datetime



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

    @api.onchange('calculation_date')
    def _onchange_date(self):
        date2 = datetime.datetime.strptime(self.calculation_date, '%Y-%m-%d') - datetime.timedelta(days=1)

        self.env.cr.execute(
            """select  net_amount from capital_drawing where calculation_date=%s order by calculation_date desc limit 1""",(date2,) )

        date= self.env.cr.fetchone()
        if date[0] is None:
            raise UserError(_('Capital drawings missing for past days with referernce to create date, please create capital drawings for missing date'))

        else:
            self.env.cr.execute(
            """select  net_amount from capital_drawing order by calculation_date desc limit 1""",)

            net_amnt = self.env.cr.fetchone()

            if net_amnt[0] is None:
                #date3 = value[0]
                self.previous_balance = 0

            else:
                self.previous_balance = net_amnt[0]








