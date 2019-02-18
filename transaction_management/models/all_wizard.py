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
        if cc_payment.commission_pay < self.rec_amount:
            raise UserError(_('Commission remaining to pay is %f, please change the amount')%(cc_payment.commission_pay))


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
                          'payment_ref': [(4, receipt_voucher.id)]
                          })



class ProcessDeposit(models.TransientModel):
    _name = "process.deposit.wizard"

    rec_date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    rec_amount = fields.Float(string='Amount Deposited')

    @api.multi
    def dep_pay(self):
        cc_payment = self.env['cc.payment'].browse(self.env.context.get('active_id'))
        if cc_payment.amount_to_deposit < self.rec_amount:
            raise UserError(_('Amount remaining to deposit is %f, please change the amount')%(cc_payment.amount_to_deposit))

        vals = {
            'journal_id': cc_payment.machine_name.branch.cash_journal_id.id,
            'partner_id': cc_payment.customer.id,
            'transaction_date': self.rec_date,
            'account_id': cc_payment.customer.property_account_receivable_id.id,
            'amount': self.rec_amount
        }
        payment_voucher = self.env['payment.voucher'].create(vals)
        payment_voucher.post()
        cc_payment.write({
                          'amount_deposited': cc_payment.amount_deposited + self.rec_amount,
                          'amount_to_deposit': cc_payment.amount_to_deposit - self.rec_amount,

                          'deposit_ref': [(4, payment_voucher.id)]
                          })


class SwipeCard(models.TransientModel):
    _name = "swipe.card.wizard"

    rec_date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    rec_amount = fields.Float(string='Amount Swiped')

    @api.multi
    def swipe(self):
        cc_payment = self.env['cc.payment'].browse(self.env.context.get('active_id'))
        if cc_payment.total_to_swipe < self.rec_amount:
            raise UserError(_('Amount remaining to swipe is %f, please change the amount')%(cc_payment.total_to_swipe))

        vals = {
            'machine_name': cc_payment.machine_name.id,
            'transaction_amount': self.rec_amount,
            'commission_included': True,
            'transaction_date': self.rec_date,
            'amount_to_swipe': self.rec_amount,
            'cost_percentage': cc_payment.machine_name.cost_percentage,
            'sales_percentage': cc_payment.commission,
            'commission': ('amount_to_swipe' * cc_payment.commission / 100),
            'cost_to_commission': ('amount_to_swipe' * 'cost_percentage' / 100),
            'parent_percentage': cc_payment.machine_name.parent_name.cost_percentage or 0,
            'cost_to_parent': ('amount_to_swipe' * 'parent_percentage' / 100),
            'margin': 'commission' - 'cost_to_commission',
            'cash_paid_customer': 0.0,
            'amount_to_customer': 'amount_to_swipe' - 'commission',
            'balance': 'amount_to_customer',
            'customer': cc_payment.customer.id,
            'parent_percentage': cc_payment,
            'customer_mobile': cc_payment.customer_mobile,
            'note': cc_payment.note

        }
        trans_master = self.env['trans.master'].create(vals)
        trans_master.post()
        cc_payment.write({
                          'total_to_swipe': cc_payment.total_to_swipe - self.rec_amount,
                          'amount_swiped': cc_payment.amount_swiped + self.rec_amount,
                          'transaction_ref': [(4, trans_master.id)]
                          })



