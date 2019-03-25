from odoo import fields, api, models, _
from odoo.exceptions import UserError


class daily_report_statement(models.TransientModel):
    _name = "daily.report.statement"
    _description = "Daily Report Summary"

    report_date = fields.Date(string='Date From', default=fields.Date.context_today, required=True)


    def print_report(self, data):


        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'transaction_management.report_daily_summary_template'
        }

