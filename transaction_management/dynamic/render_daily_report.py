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

        move_dic={}
        move_list=[]



        report_obj = self.env['daily.report.statement']
        moveline_obj=self.env['account.move.line']
        ledger_data=report_obj.browse(docids)

        self.env.cr.execute(
            """select company_id from company_branch where id=%s""",(ledger_data.branch_name.id,))
        vvalue = self.env.cr.fetchone()
        if vvalue is None:
            cid = 0
        else:
            cid = vvalue[0]


        self.env.cr.execute("""select (select name from res_partner where id=a.partner_id) as partner, sum(a.debit-a.credit) as balance from account_move_line as a left join
         account_move as b on a.move_id=b.id where a.account_id=%s and b.company_id=%s and b.state='posted' and a.date<=%s group by 
         a.partner_id """,(ledger_data.branch_name.acc_rec_id.id,cid,datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),))
        datass = self.env.cr.fetchall()


        for moveline_data in datass:
            if moveline_data[1] != 0:

                move_dic['customer']=moveline_data[0]
                move_dic['balance']=moveline_data[1]

                move_list.append(move_dic)
                move_dic={}
        
        data=move_list

        move_dic1 = {}
        move_list1 = []

        self.env.cr.execute("""select (select name from res_partner where id=a.partner_id) as partner, sum(a.debit-a.credit) as balance from account_move_line as a left join
                 account_move as b on a.move_id=b.id where a.account_id=%s and b.company_id=%s and b.state='posted' and a.date<=%s group by 
                 a.partner_id """, (
        ledger_data.branch_name.acc_payable_id.id, cid, datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),))
        datass1 = self.env.cr.fetchall()

        for moveline_data1 in datass1:
            if moveline_data1[1] != 0:
                move_dic1['vendor'] = moveline_data[0]
                move_dic1['balance'] = moveline_data[1]

                move_list1.append(move_dic1)
                move_dic1 = {}

        data1 = move_list1


        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data,
            'report_date':ledger_data.report_date,
            'branch_name':ledger_data.branch_name,
            'docs': docs,
        }
        return self.env['report'].render('transaction_management.report_daily_summary_template', docargs)
