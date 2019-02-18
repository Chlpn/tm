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
        if cc_payment.state == 'up':
            if (cc_payment.amount_to_deposit -self.rec_amount) == 0:
                chstate = 'fd'
            else:
                chstate = 'pd'

        vals = {
            'journal_id': cc_payment.machine_name.branch.cash_journal_id.id,
            'partner_id': cc_payment.customer.id,
            'transaction_date': self.rec_date,
            'account_id': cc_payment.customer.property_account_receivable_id.id,
            'amount': self.rec_amount
        }
        payment_voucher = self.env['payment.voucher'].create(vals)
        payment_voucher.post()
        cc_payment.write({ 'state': chstate,
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
        if cc_payment.machine_name.rent_again:
            par_cost = cc_payment.machine_name.parent_name.cost_percentage
        else:
            par_cost = 0.0

        if cc_payment.state == 'pd' or cc_payment.state == 'fd':
            if (cc_payment.total_to_swipe -self.rec_amount) == 0:
                chstate = 'fs'
            else:
                chstate = 'ps'

        vals = {
            'machine_name': cc_payment.machine_name.id,
            'transaction_amount': self.rec_amount,
            'commission_included': True,
            'transaction_date': self.rec_date,
            'amount_to_swipe': self.rec_amount,
            'cost_percentage': cc_payment.machine_name.cost_percentage,
            'sales_percentage': cc_payment.commission,
            'commission': (self.rec_amount * cc_payment.commission / 100.0),
            'cost_to_commission': (self.rec_amount * cc_payment.machine_name.cost_percentage / 100.0),
            'parent_percentage': par_cost,
            'cost_to_parent': (self.rec_amount * par_cost / 100.0),
            'margin': (self.rec_amount * cc_payment.commission / 100.0) - (self.rec_amount * cc_payment.machine_name.cost_percentage / 100.0),
            'cash_paid_customer': 0.0,
            'amount_to_customer': self.rec_amount - (self.rec_amount * cc_payment.commission / 100.0),
            'balance': self.rec_amount - (self.rec_amount * cc_payment.commission / 100.0),
            'customer': cc_payment.customer.id,
            'customer_mobile': cc_payment.customer_mobile,
            'note': cc_payment.note

        }
        trans_master = self.env['trans.master'].create(vals)
        trans_master.post()
        cc_payment.write({'state':chstate,
                          'total_to_swipe': cc_payment.total_to_swipe - self.rec_amount,
                          'amount_swiped': cc_payment.amount_swiped + self.rec_amount,
                          'transaction_ref': [(4, trans_master.id)]
                          })



