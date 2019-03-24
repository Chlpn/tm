from odoo import fields, api, models, _
from odoo.exceptions import UserError


class custom_customer_statement(models.TransientModel):
    _name = "custom.customer.statement"
    _description = "Custom Ledger"

    partner_id = fields.Many2one('res.partner', string="Customer", domain=[('customer', '=', True)], required=True)
    account_id = fields.Many2one('account.account', string="Account", required=True)
    date_from = fields.Date(string='Date From', default=fields.Date.context_today, required=True)
    date_to = fields.Date(string='Date To', default=fields.Date.context_today, required=True)

    @api.onchange('partner_id')
    def _onchange_partner(self):

        if self.partner_id.customer:
            self.account_id = self.partner_id.property_account_receivable_id
        elif self.partner_id.supplier:
            self.account_id = self.partner_id.property_account_payable_id

        else:
            pass


    def print_report(self, data):


        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'account_reporting.statement_customerwise_print_report'
        } 
#        data = self.pre_print_report(data)
#        data['form'].update({'reconciled': self.reconciled, 'amount_currency': self.amount_currency})
#        return self.env['report'].get_action(self, 'account.report_partnercustomer_statement', data=data)


