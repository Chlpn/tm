# -*- coding: utf-8 -*-

from odoo import fields, models


class branch(models.Model):
    _inherit = ["res.company"]
    _name = "company.branch"

    cash_ac = fields.Many2one('account.account', string="Cash Account", required=True, ondelete='restrict',
                              domain=lambda self: [
                                  ('user_type_id', '=', self.env.ref('account.data_account_type_liquidity').id)])
    journal_id = fields.Many2one('account.journal', string="Journal", ondelete='restrict', required=True)
