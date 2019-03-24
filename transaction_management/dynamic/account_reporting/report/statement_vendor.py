# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.tools import float_is_zero
from datetime import datetime

from dateutil.relativedelta import relativedelta
import datetime

class render_ldger(models.AbstractModel):

    _name = 'report.account_reporting.statement_vendorwise_print_report'


    @api.model
    def render_html(self, docids, data=None):
        print'docids==',docids
        move_dic={}
        move_list=[]
        
        general_ledger_report_obj=self.env['custom.vendor.statement']
        moveline_obj=self.env['account.move.line']
        ledger_data=general_ledger_report_obj.browse(docids)
        self.env.cr.execute("""select a.partner_id, a.date,a.name,a.debit as debit, a.credit, a.debit-a.credit as balance from account_move_line as a left join account_move as b on a.move_id=b.id where a.partner_id=%s and a.account_id=%s and   b.state='posted' and a.date>=%s and a.date<=%s order by a.date""",(ledger_data.partner_id.id,ledger_data.account_id.id,datetime.datetime.strptime(ledger_data.date_from, '%Y-%m-%d'),datetime.datetime.strptime(ledger_data.date_to, '%Y-%m-%d'),))
        datass = self.env.cr.fetchall()
        print datass
        

#        moveline_datas=moveline_obj.search([('account_id','=',ledger_data.account_id.id),('date','>=',ledger_data.date_from),('date','<=', ledger_data.date_to)])
#        print'----',moveline_datas
        self.env.cr.execute("""select sum(debit)-sum(credit) as opening_balance from account_move_line as a left join account_move as b on a.move_id=b.id where a.partner_id=%s and a.account_id=%s and  b.state='posted' and a.date<%s""",(ledger_data.partner_id.id,ledger_data.account_id.id,datetime.datetime.strptime(ledger_data.date_from, '%Y-%m-%d'),))
#        self.env.cr.execute("""select sum(debit)-sum(credit) as opening_balance from account_move_line as a left join account_move as b on a.move_id=b.id where a.account_id=184 and  b.state='posted' and a.date<'2018-01-10';""")
#        print'jjj',datetime.datetime.strptime(ledger_data.date_from, '%Y-%m-%d')
#        query = """SELECT * from account_move_line where date= %s;"""
#        self.env.cr.execute(query, (ledger_data.date_from))
        openin_balance = self.env.cr.fetchone()[0]
        print 'openin_balance=====',openin_balance
        if openin_balance is None:
            openin_balance=0.0
        closing_balance=0.0
        for moveline_data in datass:
            print'moveline_data===',moveline_data,moveline_data[0]
            move_dic['date']=moveline_data[1]
            move_dic['account']=ledger_data.partner_id.name
            move_dic['particulars']=moveline_data[2]
            move_dic['debit']=moveline_data[3]
            move_dic['credit']=moveline_data[4]
            move_dic['balance']=moveline_data[5]
            closing_balance=moveline_data[5]
            move_list.append(move_dic)
            move_dic={}
        
        data=move_list
        print'----',data
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        docargs = {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data,
            'date_to':ledger_data.date_to,
            'date_from':ledger_data.date_from,
            'openin_balance':openin_balance,
            'closing_balance':closing_balance,
            'partner_name': ledger_data.partner_id.name,
            'account_name':ledger_data.account_id.name,
            'docs': docs,
        }
        return self.env['report'].render('account_reporting.statement_vendorwise_print_report', docargs)
