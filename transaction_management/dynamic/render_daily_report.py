# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.tools import float_is_zero
from datetime import datetime

from dateutil.relativedelta import relativedelta
import datetime


class render_ldger(models.AbstractModel):
    _name = 'report.transaction_management.report_daily_summary_template'

    @api.model
    def render_html(self, docids, data=None):

        move_dic = {}
        move_list = []

        report_obj = self.env['daily.report.statement']
        moveline_obj = self.env['account.move.line']
        ledger_data = report_obj.browse(docids)
        # fetch company_id
        self.env.cr.execute(
            """select company_id from company_branch where id=%s""", (ledger_data.branch_name.id,))
        vvalue = self.env.cr.fetchone()
        if vvalue is None:
            cid = 0
        else:
            cid = vvalue[0]
        # fetch cash opening balance
        self.env.cr.execute(
            """select sum(debit)-sum(credit) as opening_balance from account_move_line as a left join account_move as b on a.move_id=b.id where a.account_id=%s and a.company_id=%s and  b.state='posted' and a.date<%s""",
            (ledger_data.branch_name.cash_ac.id, cid, datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),))
        op = self.env.cr.fetchone()
        if op is None:
            cob = 0
        else:
            cob = op[0]
        # fetch cash payments
        self.env.cr.execute(
            """select sum(amount) as amount from payment_voucher as a left join account_account as b on a.account_id=b.id where a.state='post' and b.company_id=%s and transaction_date=%s""",
            (cid, datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),))
        pv = self.env.cr.fetchone()
        if type(pv[0]) is float:
            pamnt = pv[0]
        else:
            pamnt = 0
        # fetch cash receipts
        self.env.cr.execute(
            """select sum(amount) as amount from receipt_voucher as a left join account_account as b on a.account_id=b.id where a.state='post' and b.company_id=%s and transaction_date=%s""",
            (cid, datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),))
        rv = self.env.cr.fetchone()
        if rv is None:
            ramnt = 0
        else:
            ramnt = rv[0]

        # fetch commission received
        self.env.cr.execute(
            """select sum(debit)-sum(credit) as commission from account_move_line as a left join account_move as b on a.move_id=b.id where a.account_id=%s and a.company_id=%s and  b.state='posted' and a.date=%s""",
            (ledger_data.branch_name.income_ac.id, cid,
             datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),))
        commnr = self.env.cr.fetchone()
        if commnr is None:
            core = 0
        else:
            core = commnr[0]

        # fetch rent to branch income
        self.env.cr.execute(
            """select sum(debit)-sum(credit) as commission from account_move_line as a left join account_move as b on a.move_id=b.id where a.account_id=%s and a.company_id=%s and  b.state='posted' and a.date=%s""",
            (ledger_data.branch_name.rentagain_income_ac.id, cid,
             datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),))
        rag = self.env.cr.fetchone()
        if type(rag[0]) is float:
            rg = rag[0]
        else:
            rg = 0

        # fetch commission expenses
        self.env.cr.execute(
            """select sum(debit)-sum(credit) as commission from account_move_line as a left join account_move as b on a.move_id=b.id where a.account_id=%s and a.company_id=%s and  b.state='posted' and a.date=%s""",
            (ledger_data.branch_name.cost_ac.id, cid,
             datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),))
        cost = self.env.cr.fetchone()
        if cost is None:
            ce = 0
        else:
            ce = cost[0]


        # fetch general expenses
        self.env.cr.execute(
            """select sum(debit)-sum(credit) as expense from account_move_line as a left join account_account as b on a.account_id=b.id left join account_move as c on a.move_id = c.id where b.user_type_id = 16 and c.state='posted' and a.company_id=%s and a.date=%s""",
            (cid, datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),))
        gen = self.env.cr.fetchone()
        if type(gen[0]) is float:
            gex = gen[0]
        else:
            gex = 0

        # fetch cash closing balance
        self.env.cr.execute(
            """select sum(debit)-sum(credit) as opening_balance from account_move_line as a left join account_move as b on a.move_id=b.id where a.account_id=%s and a.company_id=%s and  b.state='posted' and a.date<=%s""",
            (ledger_data.branch_name.cash_ac.id, cid,
             datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),))
        cl = self.env.cr.fetchone()
        if cl is None:
            ccb = 0
        else:
            ccb = cl[0]

        # fetch customer balance

        self.env.cr.execute("""select (select name from res_partner where id=a.partner_id) as partner, sum(a.debit-a.credit) as balance from account_move_line as a left join
         account_move as b on a.move_id=b.id where a.account_id=%s and b.company_id=%s and b.state='posted' and a.date<=%s group by 
         a.partner_id """, (
        ledger_data.branch_name.acc_rec_id.id, cid, datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),))
        datass = self.env.cr.fetchall()

        for moveline_data in datass:
            if moveline_data[1] != 0:
                move_dic['customer'] = moveline_data[0]
                move_dic['balance'] = moveline_data[1]

                move_list.append(move_dic)
                move_dic = {}

        data = move_list

        # fetch vendor balance

        move_dic1 = {}
        move_list1 = []

        self.env.cr.execute("""select (select name from res_partner where id=a.partner_id) as partner, sum(a.debit-a.credit) as balance from account_move_line as a left join
                 account_move as b on a.move_id=b.id where a.account_id=%s and b.company_id=%s and b.state='posted' and a.date<=%s group by 
                 a.partner_id """, (
            ledger_data.branch_name.acc_payable_id.id, cid,
            datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),))
        datass1 = self.env.cr.fetchall()

        for moveline_data1 in datass1:
            if moveline_data1[1] != 0:
                move_dic1['vendor'] = moveline_data1[0]
                move_dic1['balance'] = moveline_data1[1]

                move_list1.append(move_dic1)
                move_dic1 = {}

        data1 = move_list1
        # fetch Bank Balance

        move_dicbnk = {}
        move_listbnk = []

        self.env.cr.execute("""select name, (select sum(debit)-sum(credit) from account_move_line as a left join account_account as b on a.account_id=b.id left join account_move as c on a.move_id = c.id where c.state='posted' and a.company_id=%s and a.date<=%s and a.account_id=aa.id)as Opening_balance, (select sum(debit) from account_move_line as a left join account_account as b on a.account_id=b.id left join account_move as c on a.move_id = c.id where c.state='posted' and a.company_id=%s and a.date=%s and a.account_id=aa.id)as Debit, (select sum(credit) from account_move_line as a left join account_account as b on a.account_id=b.id left join account_move as c on a.move_id = c.id where c.state='posted' and a.company_id=%s and a.date=%s and a.account_id=aa.id)as Credit, (select sum(debit)-sum(credit) from account_move_line as a left join account_account as b on a.account_id=b.id left join account_move as c on a.move_id = c.id where c.state='posted' and a.company_id=%s and a.date<=%s and a.account_id=aa.id)as Closing_balance from account_account as aa where user_type_id=3""",
                            (
                                cid,ledger_data.report_date2,cid,datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),cid,datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),cid,datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),))
        datassbnk = self.env.cr.fetchall()

        for moveline_databnk in datassbnk:
            move_dicbnk['bank'] = moveline_databnk[0]
            move_dicbnk['opening'] = moveline_databnk[1]
            move_dicbnk['debit'] = moveline_databnk[2]
            move_dicbnk['credit'] = moveline_databnk[3]
            move_dicbnk['closing'] = moveline_databnk[4]

            move_listbnk.append(move_dicbnk)
            move_dicbnk = {}

        databnk = move_listbnk

        # fetch Merchant Balance

        move_dicmer = {}
        move_listmer = []

        self.env.cr.execute(
            """select name, (select sum(debit)-sum(credit) from account_move_line as a left join account_account as b on a.account_id=b.id left join account_move as c on a.move_id = c.id where c.state='posted' and a.company_id=%s and a.date<=%s and a.account_id=aa.id)as Opening_balance, (select sum(debit) from account_move_line as a left join account_account as b on a.account_id=b.id left join account_move as c on a.move_id = c.id where c.state='posted' and a.company_id=%s and a.date=%s and a.account_id=aa.id)as Debit, (select sum(credit) from account_move_line as a left join account_account as b on a.account_id=b.id left join account_move as c on a.move_id = c.id where c.state='posted' and a.company_id=%s and a.date=%s and a.account_id=aa.id)as Credit, (select sum(debit)-sum(credit) from account_move_line as a left join account_account as b on a.account_id=b.id left join account_move as c on a.move_id = c.id where c.state='posted' and a.company_id=%s and a.date<=%s and a.account_id=aa.id)as Closing_balance from account_account as aa where user_type_id=4""",
            (
                cid, ledger_data.report_date2, cid, datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),
                cid, datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'), cid,
                datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),))
        datassmer = self.env.cr.fetchall()

        for moveline_datamer in datassmer:
            move_dicmer['bank'] = moveline_datamer[0]
            move_dicmer['opening'] = moveline_datamer[1]
            move_dicmer['debit'] = moveline_datamer[2]
            move_dicmer['credit'] = moveline_datamer[3]
            move_dicmer['closing'] = moveline_datamer[4]

            move_listmer.append(move_dicmer)
            move_dicmer = {}

        datamer = move_listmer
        # fetch machine balance

        # fetch machine balance All
        move_dica = {}
        move_lista = []

        self.env.cr.execute("""select (select name from machine_master where id=machine_name) as machine_name,sum(amount_to_swipe) 
                as amount_to_swipe,sum(amount_to_customer) as amount_to_customer,sum(cash_paid_customer) as cash_paid_customer,sum(commission) 
                as commission,sum(cost_to_commission) as cost_to_commission,sum(margin) as margin from trans_master where transaction_date=%s and state='posted' group by machine_name""", (
            datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),))
        datassa = self.env.cr.fetchall()

        for moveline_dataa in datassa:
            move_dica['machine'] = moveline_dataa[0]
            move_dica['amount_swiped'] = moveline_dataa[1]
            move_dica['amount_pay'] = moveline_dataa[2]
            move_dica['amount_paid'] = moveline_dataa[3]
            move_dica['commission'] = moveline_dataa[4]
            move_dica['cost_commission'] = moveline_dataa[5]
            move_dica['margin'] = moveline_dataa[6]

            move_lista.append(move_dica)
            move_dica = {}

        dataa = move_lista
        # fetch machine balance Abu Dhabi
        move_dic2 = {}
        move_list2 = []

        self.env.cr.execute("""select (select name from machine_master where id=machine_name) as machine_name,sum(amount_to_swipe) 
                as amount_to_swipe,sum(amount_to_customer) as amount_to_customer,sum(cash_paid_customer) as cash_paid_customer,sum(commission) 
                as commission,sum(cost_to_commission) as cost_to_commission,sum(margin) as margin from trans_master where company_id=%s 
                and transaction_date=%s and state='posted' group by machine_name""", (
            cid, datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),))
        datass2 = self.env.cr.fetchall()

        for moveline_data2 in datass2:
            move_dic2['machine'] = moveline_data2[0]
            move_dic2['amount_swiped'] = moveline_data2[1]
            move_dic2['amount_pay'] = moveline_data2[2]
            move_dic2['amount_paid'] = moveline_data2[3]
            move_dic2['commission'] = moveline_data2[4]
            move_dic2['cost_commission'] = moveline_data2[5]
            move_dic2['margin'] = moveline_data2[6]

            move_list2.append(move_dic2)
            move_dic2 = {}

        data2 = move_list2
        # fetch machine balance Own Machine
        move_dicb = {}
        move_listb = []

        self.env.cr.execute("""select (select name from machine_master where id=machine_name) as machine_name,sum(amount_to_swipe) 
                as amount_to_swipe,sum(amount_to_customer) as amount_to_customer,sum(cash_paid_customer) as cash_paid_customer,sum(commission) 
                as commission,sum(cost_to_commission) as cost_to_commission,sum(margin) as margin from trans_master as a inner join machine_master as b 
                on a.machine_name=b.id where b.company_owned=True and transaction_date=%s and state='posted' group by machine_name""", (
            datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),))
        datassb = self.env.cr.fetchall()

        for moveline_datab in datassb:
            move_dicb['machine'] = moveline_datab[0]
            move_dicb['amount_swiped'] = moveline_datab[1]
            move_dicb['amount_pay'] = moveline_datab[2]
            move_dicb['amount_paid'] = moveline_datab[3]
            move_dicb['commission'] = moveline_datab[4]
            move_dicb['cost_commission'] = moveline_datab[5]
            move_dicb['margin'] = moveline_datab[6]

            move_listb.append(move_dicb)
            move_dicb = {}

        datab = move_listb


        # fetch payment vouchers

        move_dic3 = {}
        move_list3 = []

        self.env.cr.execute(
            """select (select name from res_partner where id=a.partner_id) as part,(select name from account_account where id=a.account_id) as pacc,sum(amount) from payment_voucher as a inner join account_account as b on a.account_id=b.id where a.state='post' and b.company_id=%s and transaction_date=%s group by partner_id,account_id order by pacc,part""",
            (
                cid, datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),))
        datass3 = self.env.cr.fetchall()

        for moveline_data3 in datass3:
            move_dic3['partner'] = moveline_data3[0]
            move_dic3['account'] = moveline_data3[1]
            move_dic3['amount'] = moveline_data3[2]

            move_list3.append(move_dic3)
            move_dic3 = {}

        data3 = move_list3

        # fetch receipt vouchers

        move_dic4 = {}
        move_list4 = []

        self.env.cr.execute(
            """select (select name from res_partner where id=a.partner_id) as part,(select name from account_account where id=a.account_id) as pacc,sum(amount) from receipt_voucher as a inner join account_account as b on a.account_id=b.id where a.state='post' and b.company_id=%s and transaction_date=%s group by partner_id,account_id order by pacc,part""",
            (
                cid, datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),))
        datass4 = self.env.cr.fetchall()

        for moveline_data4 in datass4:
            move_dic4['partner'] = moveline_data4[0]
            move_dic4['account'] = moveline_data4[1]
            move_dic4['amount'] = moveline_data4[2]

            move_list4.append(move_dic4)
            move_dic4 = {}

        data4 = move_list4

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'cob': cob,
            'ccb': ccb,
            'ramnt': ramnt,
            'pamnt': pamnt,
            'core': core,
            'rg': rg,
            'ce': ce,
            'gex': gex,
            'data': data,
            'data1': data1,
            'data2': data2,
            'data3': data3,
            'data4': data4,
            'dataa': dataa,
            'datab': datab,
            'databnk': databnk,
            'datamer': datamer,
            'report_date': ledger_data.report_date,
            'branch_name': ledger_data.branch_name,
            'docs': docs,
        }
        return self.env['report'].render('transaction_management.report_daily_summary_template', docargs)
