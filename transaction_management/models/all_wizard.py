# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class ReceiveCommission(models.TransientModel):
    _name = "receive.commission.wizard"

    rec_date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    rec_amount = fields.Float(string='Amount')

    @api.multi
    def rec_com(self):
        cc_payment = self.env['cc.payment'].browse(self.env.context.get('active_id'))
        vals = {
                   'journal_id':cc_payment.machine_name.branch.cash_journal_id,
                    'partner_id':cc_payment.customer,
                    'transaction_date':self.rec_date,
                    'account_id':cc_payment.customer.property_account_receivable_id,
                    'amount': self.rec_amount
        }
        receipt_voucher = self.env['receipt.voucher'].create(vals)
        receipt_voucher.post()
        cc_payment.write({'state': 'up',
                          'commission_paid': cc_payment.commission_paid + self.rec_amount,
                          'commission_pay': cc_payment.commission_pay - self.rec_amount,
                          'total_to_swipe': cc_payment.total_to_swipe - self.rec_amount,
                          'payment_ref': receipt_voucher.voucher_name
                          })
