# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
from datetime import datetime


class ReceiveCommission(models.TransientModel):
    _name = "receive.commission.wizard"
    
    company_id = fields.Many2one(
        'res.company',
        'Company',
        default=lambda self: self.env.user.company_id
    )


    rec_date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    rec_amount = fields.Float(string='Amount')

    @api.multi
    def rec_com(self):
        cc_payment = self.env['cc.payment'].browse(self.env.context.get('active_id'))
        chstate = cc_payment.state
        #if cc_payment.commission_pay < self.rec_amount:
            #raise UserError(_('Commission remaining to pay is %f, please change the amount')%(cc_payment.commission_pay))
        self.env.cr.execute(
                    """select cash_journal_id from company_branch where company_id=%s""",
                    (self.company_id.id,))

        value = self.env.cr.fetchone()
        cjournal = value[0]


        vals = {
                   'journal_id':cjournal,
                    'partner_id':cc_payment.customer.id,
                    'transaction_date':self.rec_date,
                    'account_id':cc_payment.customer.property_account_receivable_id.id,
                    'amount': self.rec_amount,
                    'description': 'credit card payment-' + cc_payment.serial,
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
    
    company_id = fields.Many2one(
        'res.company',
        'Company',
        default=lambda self: self.env.user.company_id
    )


    rec_date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    rec_amount = fields.Float(string='Amount Deposited')

    @api.multi
    def dep_pay(self):
        cc_payment = self.env['cc.payment'].browse(self.env.context.get('active_id'))
        chstate = cc_payment.state
        #if cc_payment.amount_to_deposit < self.rec_amount:
            #raise UserError(_('Amount remaining to deposit is %f, please change the amount')%(cc_payment.amount_to_deposit))
        if cc_payment.state == 'up' or cc_payment.state == 'pd':
            if (cc_payment.amount_to_deposit -self.rec_amount) == 0:
                chstate = 'fd'
            else:
                chstate = 'pd'
        elif cc_payment.state == 'dr':
            chstate = 'up'

        self.env.cr.execute(
                    """select cash_journal_id from company_branch where company_id=%s""",
                    (self.company_id.id,))

        value = self.env.cr.fetchone()
        cjournal = value[0]

        vals = {
            'journal_id': cjournal,
            'partner_id': cc_payment.customer.id,
            'transaction_date': self.rec_date,
            'account_id': cc_payment.customer.property_account_receivable_id.id,
            'amount': self.rec_amount,
            'description': 'credit card payment-'+ cc_payment.serial,
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

    company_id = fields.Many2one(
        'res.company',
        'Company',
        default=lambda self: self.env.user.company_id
    )

    rec_date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    machine_name = fields.Many2one('machine.master', ondelete='restrict')
    rec_amount = fields.Float(string='Amount Swiped')

    @api.multi
    def swipe(self):
        cc_payment = self.env['cc.payment'].browse(self.env.context.get('active_id'))
        chstate = cc_payment.state
        #if cc_payment.total_to_swipe < self.rec_amount:
            #raise UserError(_('Amount remaining to swipe is %f, please change the amount')%(cc_payment.total_to_swipe))
        if self.machine_name.rent_again:
            par_cost = self.machine_name.parent_name.cost_percentage
        else:
            par_cost = 0.0

        if cc_payment.state == 'pd' or cc_payment.state == 'fd' or cc_payment.state == 'ps':
            if (cc_payment.total_to_swipe -self.rec_amount) == 0:
                chstate = 'fs'
            else:
                chstate = 'ps'
        elif cc_payment.state == 'dr':
            chstate = 'up'

        vals = {
            'machine_name': self.machine_name.id,
            'transaction_amount': self.rec_amount,
            'commission_included': True,
            'transaction_date': self.rec_date,
            'amount_to_swipe': self.rec_amount,
            'cost_percentage': self.machine_name.cost_percentage,
            'sales_percentage': cc_payment.commission,
            'commission': (self.rec_amount * cc_payment.commission / 100.0),
            'cost_to_commission': (self.rec_amount * self.machine_name.cost_percentage / 100.0),
            'parent_percentage': par_cost,
            'cost_to_parent': (self.rec_amount * par_cost / 100.0),
            'margin': (self.rec_amount * cc_payment.commission / 100.0) - (self.rec_amount * self.machine_name.cost_percentage / 100.0),
            'cash_paid_customer': 0.0,
            'amount_to_customer': self.rec_amount - (self.rec_amount * cc_payment.commission / 100.0),
            'balance': self.rec_amount - (self.rec_amount * cc_payment.commission / 100.0),
            'customer': cc_payment.customer.id,
            'customer_mobile': cc_payment.customer_mobile,
            'note': cc_payment.note,
            'ccpayment_ref':cc_payment.serial

        }


        trans_master = self.env['trans.master'].create(vals)

        cc_payment.write({'state':chstate,
                          'total_to_swipe': cc_payment.total_to_swipe - self.rec_amount,
                          'amount_swiped': cc_payment.amount_swiped + self.rec_amount,
                          'transaction_ref': [(4, trans_master.id)]
                          })

    class SwipeCard2(models.TransientModel):
        _name = "swipe.card.wizard2"

        company_id = fields.Many2one(
            'res.company',
            'Company',
            default=lambda self: self.env.user.company_id
        )
        rec_amount = fields.Float(string='Amount Swiped', default='',digits=dp.get_precision('Account'))
        rec_percentage = fields.Float(string='Sales Percentage',digits=dp.get_precision('Account'))
        rec_date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
        rec_customer = fields.Many2one('res.partner', string="Customer", ondelete='restrict')
        rec_customer_mobile = fields.Char(related='rec_customer.mobile', string='Mobile')
        rec_amount_to_customer = fields.Float(string='Amount to customer', store=True, digits=dp.get_precision('Account'))
        rec_cash_paid_customer = fields.Float(string='Cash Paid', digits=dp.get_precision('Account'))
        rec_balance = fields.Float(string='Balance', digits=dp.get_precision('Account'))
        rec_commission = fields.Float(string='Commission', digits=dp.get_precision('Account'))
        rec_cost_to_commission = fields.Float(string='Cost of Commission', digits=dp.get_precision('Account'))
        rec_par_cost = fields.Float(string='Cost of Commission', digits=dp.get_precision('Account'))
        rec_cost_percentage = fields.Float(string='Cost Precentage', digits=dp.get_precision('Account'))
        rec_cost_to_parent = fields.Float(string='Cost Precentage', digits=dp.get_precision('Account'))



        @api.onchange('rec_amount','rec_percentage')
        def _onchange_amount_to_customer(self):
            mm_master = self.env['machine.master'].browse(self.env.context.get('active_id'))

            self.rec_cost_percentage = mm_master.cost_percentage
            self.rec_commission = (self.rec_amount * self.rec_percentage / 100)
            self.rec_cost_to_commission = (self.rec_amount * self.rec_cost_percentage / 100.0)
            self.rec_amount_to_customer = (self.rec_amount - self.rec_commission)
            self.rec_cash_paid_customer = self.rec_amount_to_customer
            self.rec_balance = self.rec_amount_to_customer - self.rec_cash_paid_customer

            if mm_master.machine_name.rent_again & self.env['res.users'].has_group('account.group_account_manager'):
                self.rec_par_cost = mm_master.parent_name.cost_percentage
            else:
                self.rec_par_cost = 0.0
            self.rec_cost_to_parent = (self.rec_amount * self.rec_par_cost / 100.0)


        @api.onchange('rec_cash_paid_customer')
        def _cash_paid_customer(self):
            self.rec_balance = self.rec_amount_to_customer - self.rec_cash_paid_customer

        @api.multi
        def swipe2(self):

            mm_master = self.env['machine.master'].browse(self.env.context.get('active_id'))

            vals = {
                'machine_name': mm_master.id,
                'transaction_amount': self.rec_amount,
                'commission_included': True,
                'transaction_date': self.rec_date,
                'amount_to_swipe': self.rec_amount,
                'cost_percentage': self.rec_cost_percentage,
                'sales_percentage': self.rec_percentage,
                'commission': self.rec_commission,
                'cost_to_commission': self.rec_cost_to_commission,
                'parent_percentage': self.rec_par_cost,
                'cost_to_parent': self.rec_cost_to_parent,
                'margin': self.rec_commission - self.rec_cost_to_commission,
                'amount_to_customer': self.rec_amount_to_customer,
                'cash_paid_customer': self.rec_cash_paid_customer,
                'balance': self.rec_balance,
                'customer': self.rec_customer.id,
                'customer_mobile': self.rec_customer_mobile,



            }

            trans_master2 = self.env['trans.master'].create(vals)

            mm_master.swipe_card()



