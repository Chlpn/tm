from odoo import fields,models
from datetime import datetime


class DailyReport(models.TransientModel):
    _name = "daily.report"

    report_date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    report_branch = fields.Many2one('company.branch', string="branch", required=True)