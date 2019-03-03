from odoo import fields,models,api
from datetime import datetime


class DailyReport(models.TransientModel):
    _name = "daily.report"

    report_date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    report_branch = fields.Many2one('company.branch', string="branch", required=True)
    cash_op_bal =fields.Float()




    def daily_print_method(self):

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'transaction_management.daily_print_report'
        }

    @api.multi
    @api.onchange('report_date','report_branch')
    def calc_values(self):
        if self.report_branch:
            print self.report_branch.cash_ac.id
            print datetime.strptime(self.report_date, '%Y-%m-%d')
            self.env.cr.execute("""select sum(debit-credit) from account_move_line where account_id=%s and date<%s""",
                            (self.report_branch.cash_ac.id, datetime.strptime(self.report_date, '%Y-%m-%d')))
            self.cash_op_bal = self.env.cr.fetchone()[0]

            if self.cash_op_bal is None:
                self.cash_op_bal = 0.0

        