from odoo import fields, api, models, _
from odoo.exceptions import UserError


class daily_report_statement(models.TransientModel):
    _name = "daily.report.statement"
    _description = "Daily Report Summary"

    branch_name = fields.Many2one('company.branch', string="Branch", required=True)
    report_date = fields.Date(string='Date From', default=fields.Date.context_today, required=True)
    report_date2 = fields.Date(string='Date From', required=True)

    @api.onchange('report_date')
    def _onchange_date(self):
        self.report_date2 = self.report_date - 1



    def print_report(self, data):


        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'transaction_management.report_daily_summary_template'
        }

