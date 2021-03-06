# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import amount_to_text_en
import datetime



class CapitalDrawing(models.Model):
    _inherit = ["multi.company.abstract"]
    _name = "capital.drawing"

    name = fields.Char(string='Name', size=64, readonly=True)
    _sql_constraints = [('name_uniq', 'unique (name)', 'Number must be unique !')]
    calculation_date = fields.Date(string='Transaction Date', required=True, default=fields.Date.context_today)
    _sql_constraints = [('calc_date', 'unique (calculation_date)', 'only one document can be created for a paritcular date !')]
    previous_balance= fields.Float('Previous Balance' )
    gross_profit = fields.Float('Gross Profit' )
    expenses = fields.Float('Total Expenses')
    net_profit = fields.Float('Net Profit')
    lock_amount = fields.Float('received lock amount')
    gross_amount = fields.Float('Amount to Pay')
    amount_paid = fields.Float('Amount Paid')
    amount_received = fields.Float('Amount Received')
    net_amount = fields.Float('Net Balance')
    payment_ref = fields.Many2many('payment.voucher', 'cd_pay_rel', 'cdp_id', 'pay_id', 'Payment Reference')
    receipt_ref = fields.Many2many('receipt.voucher', 'cd_rec_rel', 'cdr_id', 'rec_id', 'Receipt Reference')

    bank = fields.Float('Bank Balance')
    cash = fields.Float('Cash Balance')
    mer_rec = fields.Float('Merchant Receivables')
    adv_swipe = fields.Float('Advance Swipe')
    rec = fields.Float('Total Receivables')
    loc_rec = fields.Float('Locked Receivables' )
    curr_rec = fields.Float('Current Receivable')
    liab = fields.Float('Liabilities' )
    run_cap = fields.Float('Running Capital' )
    calc_diff = fields.Float('Calculated difference' )
    deviation = fields.Float('Other deviation' )
    lock_date = fields.Date(string='Lock Date')
    lock_capital =fields.Float('Locked Capital' )

    state = fields.Selection([
        ('dr', 'Draft'),
        ('cal', 'Calculated'),
        ('pd', 'Profit Paid'),
        ('rec', 'Profit Paid & Expense Received'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='dr', readonly=True)
    _sql_constraints = [('name_uniq', 'unique (name)', 'Document Number must be unique !')]
    _defaults = {'name': lambda self, cr, uid, context: 'Capital Drawing'}

    @api.onchange('calculation_date','amount_paid','amount_received')
    def _onchange_date(self):
        date2 = datetime.datetime.strptime(self.calculation_date, '%Y-%m-%d') - datetime.timedelta(days=1)

        self.env.cr.execute(
            """select  net_amount from capital_drawing where calculation_date=%s order by calculation_date desc limit 1""",(date2,) )

        #date= self.env.cr.fetchone()
        #if date[0] is None:
           # raise UserError(_('Capital drawings missing for past days with referernce to create date, please create capital drawings for missing date'))

        #else:
        #self.env.cr.execute(
        #    """select  net_amount from capital_drawing order by calculation_date desc limit 1""",)

        net_amnt = self.env.cr.fetchone()

        if type(net_amnt[0]) is float:
            self.previous_balance = net_amnt[0]
            #date3 = value[0]


        else:
            self.previous_balance = 0

                # fetch commission received
        self.env.cr.execute(
                    """select sum(debit)-sum(credit) as commission from account_move_line as a left join account_move as b on a.move_id=b.id  left join account_account as c on a.account_id=c.id where c.user_type_id=14 and  b.state='posted' and a.date=%s""",
                    (datetime.datetime.strptime(self.calculation_date, '%Y-%m-%d'),))
        commnr = self.env.cr.fetchone()
        if commnr is None:
            core = 0
        else:
            core = commnr[0]



            # fetch commission expenses
        self.env.cr.execute(
                    """select sum(debit)-sum(credit) as commission from account_move_line as a left join account_move as b on a.move_id=b.id left join account_account as c on a.account_id=c.id where c.user_type_id=17 and  b.state='posted' and a.date=%s""",
                    (datetime.datetime.strptime(self.calculation_date, '%Y-%m-%d'),))
        cost = self.env.cr.fetchone()
        if cost is None:
            ce = 0
        else:
            ce = cost[0]
        self.gross_profit = -1*(core +ce)
            # fetch general expenses
        self.env.cr.execute(
                    """select sum(debit)-sum(credit) as expense from account_move_line as a left join account_account as b on a.account_id=b.id left join account_move as c on a.move_id = c.id where b.user_type_id = 16 and a.account_id!=84 and c.state='posted' and a.date=%s""",
                    (datetime.datetime.strptime(self.calculation_date, '%Y-%m-%d'),))
        gen = self.env.cr.fetchone()
        if type(gen[0]) is float:
            gex = gen[0]
        else:
            gex = 0

        self.expenses = gex

            # fetch lock amount
        self.env.cr.execute(
                    """select sum(amount) from receipt_voucher where locked_balance=True and transaction_date=%s and state='post'""",
                    (datetime.datetime.strptime(self.calculation_date, '%Y-%m-%d'),))
        lock_bal = self.env.cr.fetchone()
        if type(lock_bal[0]) is float:
            self.lock_amount = lock_bal[0]
        else:
            self.lock_amount = 0

        self.expenses = gex

        self.net_profit = self.gross_profit - self.expenses
        self.gross_amount = self.previous_balance+self.net_profit + self.lock_amount
        self.net_amount = self.gross_amount -self.amount_paid + self.amount_received

        # fetch cash closing balance
        self.env.cr.execute(
            """select sum(debit)-sum(credit) as opening_balance from account_move_line as a left join account_move as b on a.move_id=b.id left join account_account as c on a.account_id=c.id  where c.user_type_id=18 and  b.state='posted' and a.date<=%s""",
            (datetime.datetime.strptime(self.calculation_date, '%Y-%m-%d'),))
        cl = self.env.cr.fetchone()
        if cl is None:
            self.cash = 0
        else:
            self.cash = cl[0]

        # fetch bank closing balance
        self.env.cr.execute(
                """select sum(debit)-sum(credit) as opening_balance from account_move_line as a left join account_move as b on a.move_id=b.id left join account_account as c on a.account_id=c.id  where c.user_type_id=3 and  b.state='posted' and a.date<=%s""",
                (datetime.datetime.strptime(self.calculation_date, '%Y-%m-%d'),))
        cl = self.env.cr.fetchone()
        if cl is None:
            self.bank = 0
        else:
            self.bank = cl[0]

        # fetch merchant closing balance
        self.env.cr.execute(
                """select sum(debit)-sum(credit) as opening_balance from account_move_line as a left join account_move as b on a.move_id=b.id left join account_account as c on a.account_id=c.id  where c.user_type_id=8 and  b.state='posted' and a.date<=%s""",
                (datetime.datetime.strptime(self.calculation_date, '%Y-%m-%d'),))
        cl = self.env.cr.fetchone()
        if cl is None:
            self.mer_rec = 0
        else:
            self.mer_rec = cl[0]

        # fetch receivables balance
        self.env.cr.execute(
                """select sum(debit)-sum(credit) as opening_balance from account_move_line as a left join account_move as b on a.move_id=b.id left join account_account as c on a.account_id=c.id  where c.user_type_id=1 and  b.state='posted' and a.date<=%s""",
                (datetime.datetime.strptime(self.calculation_date, '%Y-%m-%d'),))
        cl = self.env.cr.fetchone()
        if cl is None:
            self.rec = 0
        else:
            self.rec = cl[0]

        # fetch locked capital and locked date

        self.env.cr.execute(
            """select  running_capital,capital_date,locked_rec from company_branch where company_id=1""", )
        cl = self.env.cr.fetchone()
        if cl[0] is None:
            self.lock_amount = 0

        else:
            self.lock_capital = cl[0]
            self.lock_date = cl[1]
            self.loc_rec =cl[2]





        # fetch advance payment

        self.env.cr.execute(
            """select sum(amount_to_customer) from trans_master where ccpayment_ref is NULL and cash_paid_customer=0 and transaction_date=%s and state='posted'""",
            (datetime.datetime.strptime(self.calculation_date, '%Y-%m-%d'),))
        cl = self.env.cr.fetchone()
        if cl[0] is None:
            self.adv_swipe = 0

        else:
            self.adv_swipe = cl[0]

        # fetch liabilities balance
        self.env.cr.execute(
                """select sum(debit)-sum(credit) as opening_balance from account_move_line as a left join account_move as b on a.move_id=b.id left join account_account as c on a.account_id=c.id  where c.user_type_id=2 and  b.state='posted' and a.date<=%s""",
                (datetime.datetime.strptime(self.calculation_date, '%Y-%m-%d'),))

        cl = self.env.cr.fetchone()
        if cl is None:
            self.liab = 0
        else:
            self.liab = -1 * cl[0]

        self.curr_rec = self.rec - self.loc_rec + self.adv_swipe + self.lock_amount

        self.run_cap = self.cash + self.bank + self.mer_rec -self.adv_swipe -self.net_amount-self.liab

        self.calc_diff = self.lock_capital - self.run_cap

        self.deviation = self.calc_diff -self.curr_rec