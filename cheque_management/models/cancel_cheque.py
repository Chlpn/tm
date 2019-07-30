# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class CancelCheque(models.TransientModel):
    _name = "cancel.cheque"

    comment = fields.Text(string="Comment", required=True)
    date_cancel = fields.Date(string='Cancel Date', default=fields.Date.context_today, required=True)

    @api.multi
    def cancel_cheque(self):
        cheque_obj = self.env['cheque.master'].browse(self.env.context.get('active_id'))
        if cheque_obj.state in ('new','used'):
            cheque_obj.write({'comment': self.comment, 'state': 'cancelled'})
        else:
            ir_model_obj = self.env['ir.model.data']
            model, journal_id = ir_model_obj.get_object_reference('cheque_management', 'cheque_journal')
            line_ids = [
                (0, 0,
                 {'journal_id': journal_id, 'account_id': cheque_obj.bank_name.pdc_account_id.id,
                  'name': cheque_obj.name,
                  'amount_currency': 0.0, 'debit': cheque_obj.amount}),
                (0, 0, {'journal_id': journal_id, 'account_id': cheque_obj.partner_account_id.id, 'name': '/',
                        'amount_currency': 0.0, 'credit': cheque_obj.amount, 'partner_id': cheque_obj.partner_id.commercial_partner_id})
            ]

            vals = {
                'journal_id': journal_id,
                'ref': cheque_obj.name,
                'date': self.date_cancel,
                'line_ids': line_ids,
            }
            account_move = self.env['account.move'].create(vals)
            account_move.post()
            cheque_obj.write({'comment': self.comment, 'cancel_date': self.date_cancel, 'state': 'cancelled','account_move_ids': [(4, account_move.id)],})
