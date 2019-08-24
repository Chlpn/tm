# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('line_ids')
    def _onchange_line_ids(self):
        @api.model
        def create(self, values):
            record = super(AccountMove, self)._onchange_line_ids(self)
            self.line_ids.ref = self.ref

            return record

