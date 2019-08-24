# -*- coding: utf-8 -*-

from odoo import fields, models, api


class branch(models.Model):
    _name = "company.branch"
    _rec_name = "company_id"

    company_id =fields.Many2one('res.company', string="Branch", required=True, ondelete='restrict')
    _sql_constraints = [('company_id_uniq', 'UNIQUE (company_id)', 'The branch name must be unique !')]

    cash_ac = fields.Many2one('account.account', string="Cash Account", required=True, ondelete='restrict',
                              domain=lambda self: [
                                  ('user_type_id', '=', self.env.ref('account.data_account_type_liquidity').id)])
    cost_ac = fields.Many2one('account.account', string="Cost Account", required=True, ondelete='restrict',
                              domain=lambda self: [
                                  ('user_type_id', '=', self.env.ref('account.data_account_type_direct_costs').id)])
    income_ac = fields.Many2one('account.account', string="Income Account", required=True, ondelete='restrict',
                                domain=lambda self: [
                                    ('user_type_id', '=', self.env.ref('account.data_account_type_revenue').id)])
    rentagain_income_ac = fields.Many2one('account.account', string="Rent Again Income Account", required= False, ondelete='restrict',
                                domain=lambda self: [
                                    ('user_type_id', '=', self.env.ref('account.data_account_type_revenue').id)])

    journal_id = fields.Many2one('account.journal', string="Transaction Journal", ondelete='restrict', required=True)

    cash_journal_id = fields.Many2one('account.journal', string="Cash Journal", ondelete='restrict', required=True)

    acc_payable_id = fields.Many2one('account.account', string="Accounts Payable", ondelete='restrict')
    acc_rec_id = fields.Many2one('account.account', string="Accounts Receivable", ondelete='restrict')
    running_captial = fields.Float(string='Set Running Capital')
    capital_date = fields.Date(string='Capital Date', default=fields.Date.context_today, required=True)


