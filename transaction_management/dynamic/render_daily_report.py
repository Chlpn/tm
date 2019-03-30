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


        self.env.cr.execute("""select (select name from res_partner where id=a.partner_id) as partner, sum(a.debit-a.credit) as balance from account_move_line as a left join account_move as b on a.move_id=b.id where a.account_id=19 and  b.state='posted' and a.date<=%s group by a.partner_id """,(datetime.datetime.strptime(ledger_data.report_date, '%Y-%m-%d'),))
        datass = self.env.cr.fetchall()

        

#        moveline_datas=moveline_obj.search([('account_id','=',ledger_data.account_id.id),('date','>=',wizard_data.report_date),('date','<=', wizard_data.report_date)])
#        print'----',moveline_datas
#        self.env.cr.execute("""select sum(debit)-sum(credit) as opening_balance from account_move_line as a left join account_move as b on a.move_id=b.id where a.partner_id=%s and a.account_id=%s and  b.state='posted' and a.date<%s""",(ledger_data.customer.id,ledger_data.customer.property_account_receivable_id.id,datetime.datetime.strptime(wizard_data.report_date, '%Y-%m-%d'),))
#        self.env.cr.execute("""select sum(debit)-sum(credit) as opening_balance from account_move_line as a left join account_move as b on a.move_id=b.id where a.partner_id=184 and  b.state='posted' and a.date<'2018-01-10';""")
#        print'jjj',datetime.datetime.strptime(wizard_data.report_date, '%Y-%m-%d')
#        query = """SELECT * from account_move_line where date= %s;"""
#        self.env.cr.execute(query, (wizard_data.report_date))
#        openin_balance = self.env.cr.fetchone()[0]

#        if openin_balance is None:
#            openin_balance=0.0
#        closing_balance=0.0
        for moveline_data in datass:
            if moveline_data[2] != 0:

                move_dic['customer']=moveline_data[1]
                move_dic['balance']=moveline_data[2]

                move_list.append(move_dic)
                move_dic={}
        
        data=move_list

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data,
            'report_date':ledger_data.report_date,
            'company_id':ledger_data.company_id,
            'docs': docs,
        }
        return self.env['report'].render('account_reporting.statement_customerwise_print_report', docargs)
