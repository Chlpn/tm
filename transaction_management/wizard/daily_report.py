from odoo import fields,models,api
from datetime import datetime


class DailyReport(models.TransientModel):
    _name = "daily.report"

    report_date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    report_branch = fields.Many2one('company.branch', string="branch", required=True)
    cash_op_bal =fields.Float(string="Cash Opening Balance")
    cash_cl_bal =fields.Float(string="Cash Closing Balance")
    cash_to_customer =fields.Float(string="Cash to Customer")




    def daily_print_method(self):

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'transaction_management.daily_print_report'
        }

    @api.multi
    @api.onchange('report_date','report_branch')
    def calc_values(self):
        if self.report_branch:

            self.env.cr.execute("""select sum(debit-credit) from account_move_line inner join account_move on account_move_line.move_id=accoun
      t_move.id where account_id=%s and account_move_line.date <%s and state='posted'""",
                            (self.report_branch.cash_ac.id, datetime.strptime(self.report_date, '%Y-%m-%d')))
            self.cash_op_bal = self.env.cr.fetchone()[0]

            if self.cash_op_bal is None:
                self.cash_op_bal = 0

            self.env.cr.execute("""select sum(debit-credit) from account_move_line inner join account_move on account_move_line.move_id=accoun
      t_move.id where account_id=%s and journal_id=%s and account_move_line.date =%s and state='posted'""",
                                (self.report_branch.cash_ac.id,self.report_branch.journal_id.id, datetime.strptime(self.report_date, '%Y-%m-%d')))
            self.cash_to_customer = self.env.cr.fetchone()[0]

            if self.cash_to_customer is None:
                self.cash_to_customer = 0

            self.env.cr.execute("""select sum(debit-credit) from account_move_line inner join account_move on account_move_line.move_id=accoun
      t_move.id where account_id=%s and account_move_line.date <=%s and state='posted'""",
                                (self.report_branch.cash_ac.id, datetime.strptime(self.report_date, '%Y-%m-%d')))
            self.cash_cl_bal = self.env.cr.fetchone()[0]

            if self.cash_cl_bal is None:
                self.cash_cl_bal = 0

