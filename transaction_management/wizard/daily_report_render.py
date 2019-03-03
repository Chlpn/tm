# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.tools import float_is_zero
from datetime import datetime

from dateutil.relativedelta import relativedelta
import datetime

class render_report(models.AbstractModel):

    _name = 'report.transaction_management.daily_print_report'


    @api.model
    def render_html(self, docids, data=None):
        print'docids==',docids
        move_dic={}
        move_list=[]
        
        daily_report_obj=self.env['daily.report']
        moveline_obj=self.env['account.move.line']
        daily_data=daily_report_obj.browse(docids)
        self.env.cr.execute("""select sum(debit-credit) from account_move_line where account_id=%s and date<%s""",(daily_data.report_branch.cash_ac.id,daily_data.report_date))
        cash_bal_list = self.env.cr.fetchall()[0]
        if cash_bal_list is None:
            cash_bal_list=0.0


