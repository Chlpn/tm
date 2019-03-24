from odoo import fields, api, models, _
from odoo.exceptions import UserError


class daily_report_statement(models.TransientModel):
    _name = "daily.report.statement"
    _description = "Daily Report Summary"

    report_date = fields.Date(string='Date From', default=fields.Date.context_today, required=True)


    
