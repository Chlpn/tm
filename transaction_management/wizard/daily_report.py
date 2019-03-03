from odoo import fields,models
from datetime import datetime


class DailyReport(models.TransientModel):
    _name = "daily.report"

    report_date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    report_branch = fields.Many2one('company.branch', string="branch")



    def daily_print_method(self):

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'transaction_management.daily_print_report'
        }