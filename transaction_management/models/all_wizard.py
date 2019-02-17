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
                   'journal_id':cc_payment.machine_name.branch.cash_journal_id.id,
                    'partner_id':cc_payment.customer.id,
                    'transaction_date':self.rec_date,
                    'account_id':cc_payment.customer.property_account_receivable_id.id,
                    'amount': self.rec_amount
        }
        receipt_voucher = self.env['receipt.voucher'].create(vals)
        receipt_voucher.post()
        cc_payment.write({'state': 'up',
                          'commission_paid': cc_payment.commission_paid + self.rec_amount,
                          'commission_pay': cc_payment.commission_pay - self.rec_amount,
                          'total_to_swipe': cc_payment.total_to_swipe - self.rec_amount,
                          'payment_ref': receipt_voucher.id
                          })



class ProcessDeposit(models.TransientModel):
    _name = "process.deposit.wizard"

    rec_date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    rec_amount = fields.Float(string='Amount Deposited')

    @api.multi
    def dep_pay(self):
        cc_payment = self.env['cc.payment'].browse(self.env.context.get('active_id'))
        vals = {
            'journal_id': cc_payment.machine_name.branch.cash_journal_id.id,
            'partner_id': cc_payment.customer.id,
            'transaction_date': self.rec_date,
            'account_id': cc_payment.customer.property_account_receivable_id.id,
            'amount': self.rec_amount
        }
        payment_voucher = self.env['payment.voucher'].create(vals)
        payment_voucher.post()
        cc_payment.write({'state': 'pd',
                          'amount_deposited': cc_payment.amount_deposited + self.rec_amount,
                          'amount_to_deposit': cc_payment.amount_to_deposit - self.rec_amount,

                          'deposit_ref': payment_voucher.id
                          })


class SwipeCard(models.TransientModel):
    _name = "swipe.card.wizard"

    rec_date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    rec_amount = fields.Float(string='Amount Swiped')

    @api.multi
    def rec_com(self):
        cc_payment = self.env['cc.payment'].browse(self.env.context.get('active_id'))
        vals = {
            'machine_name': cc_payment.machine_name.id,
            'transaction_amount': self.rec_amount,
            'commission_included': True,
            'transaction_date': self.rec_date,
            'customer': cc_payment.customer.id,
            'cash_paid_customer':0

        }
        trans_master = self.env['trans.master'].create(vals)
        trans_master.post()
        cc_payment.write({'state': 'ps',
                          'total_to_swipe': cc_payment.total_to_swipe - self.rec_amount,
                          'amount_swiped': cc_payment.amount_swiped + self.rec_amount,
                          'transaction_ref': trans_master.id
                          })



