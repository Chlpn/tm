# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class LostCheque(models.TransientModel):
    _name = "lost.cheque"

    date_lost = fields.Date(string='Lost Date', default=fields.Date.context_today, required=True)

    @api.multi
    def lost_cheque(self):
        cheque_obj = self.env['cheque.master'].browse(self.env.context.get('active_id'))
        if cheque_obj.state in ('used','new'):
            cheque_obj.write({'state': 'lost'})
        if cheque_obj.state in ('hold','issued', 'pending', 'printed',):
            ir_model_obj = self.env['ir.model.data']
            model, journal_id = ir_model_obj.get_object_reference('cheque_management', 'cheque_journal')
            line_ids = [
                (0, 0,
                 {'journal_id': journal_id, 'account_id': cheque_obj.bank_name.pdc_account_id.id,
                  'name': cheque_obj.name,
                  'amount_currency': 0.0, 'debit': cheque_obj.amount}),
                (0, 0, {'journal_id': journal_id, 'account_id': cheque_obj.partner_account_id.id, 'name': '/',
                        'amount_currency': 0.0, 'credit': cheque_obj.amount, 'partner_id': cheque_obj.commercial_partner_id.id})
            ]
            vals = {
                'journal_id': journal_id,
                'ref': cheque_obj.name,
                'date': self.date_lost,
                'line_ids': line_ids,
            }
            account_move = self.env['account.move'].create(vals)
            account_move.post()
            cheque_obj.write({'state': 'lost','lost_date': self.date_lost, 'account_move_ids': [(4, account_move.id)]})

