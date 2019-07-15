from odoo import fields, models, _
from odoo.exceptions import UserError


class custom_ledger(models.TransientModel):
    _name = "custom.ledger"
    _description = "Custom Ledger"

    account_id=fields.Many2one('account.account',string="Account",required=True)
    date_from = fields.Date(string='Date From', default=fields.Date.context_today, required=True)
    date_to = fields.Date(string='Date To', default=fields.Date.context_today, required=True)


    def print_report(self, data):


        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'ledger_report.ledger_print_report'
        } 
#        data = self.pre_print_report(data)
#        data['form'].update({'reconciled': self.reconciled, 'amount_currency': self.amount_currency})
#        return self.env['report'].get_action(self, 'account.report_partnerledger', data=data)


