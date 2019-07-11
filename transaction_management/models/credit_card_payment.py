# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError

class ccPayment(models.Model):
    _name = "cc.payment"
    _description = "Credit Card Payment"
    _rec_name = 'serial'

    company_id = fields.Many2one(
        'res.company',
        'Company',
        default=lambda self: self.env.user.company_id
    )
    serial = fields.Char(string='Ref. No:')
    processing_date = fields.Date(string='Date',default=fields.Date.context_today, required=True)
    payment_amount = fields.Float(string='Payment Amount', digits=dp.get_precision('Account'))
    commission = fields.Float(string='Commission Percentage', default=3.0,digits=dp.get_precision('Account'))
    commission_pay = fields.Float(string='Commission to be Paid', digits=dp.get_precision('Account'), readonly=True)
    commission_paid = fields.Float(string='Commission Paid', digits=dp.get_precision('Account'), readonly=True)
    commission_swiped = fields.Float(string='Commission Swiped', digits=dp.get_precision('Account'), readonly=True)
    swipe_commission = fields.Boolean(string='Commission to Swipe', default=False)
    total_to_swipe = fields.Float(string='Amount to Swipe', store=True, digits=dp.get_precision('Account'), readonly=True)
    payment_date = fields.Date(string='Due Date', default=fields.Date.context_today, required=True)
    amount_deposited = fields.Float(string='Amount deposited', store=True, digits=dp.get_precision('Account'), readonly=True)
    amount_to_deposit = fields.Float(string='Amount remaining to deposit', store=True, digits=dp.get_precision('Account'), readonly=True)
    #machine_name = fields.Many2one('machine.master', ondelete='restrict')
    amount_swiped = fields.Float(string='Amount swiped', store=True, digits=dp.get_precision('Account'), readonly=True)


    customer = fields.Many2one('res.partner', string="Customer", required=True, ondelete='restrict', domain=[('customer', '=', '1')])
    customer_mobile = fields.Char(related='customer.mobile',string='Mobile')
    payment_ref = fields.Many2many('receipt.voucher','cc_receipt_rel','cc_id','rec_id', 'Receipt Reference')
    deposit_ref = fields.Many2many('payment.voucher', 'cc_payment_rel','cc_id','pay_id','Deposit Reference')
    transaction_ref = fields.Many2many('trans.master', 'cc_trans_rel','cc_id','trn_id','Transaction Reference')
    note = fields.Text(string="payment_details")

    state = fields.Selection([
        ('dr', 'Draft'),
        ('up', 'Under Process'),
        ('pd', 'Partially Deposited'),
        ('fd', 'Fully Deposited'),
        ('ps', 'Partially Swiped'),
        ('fs', 'Processed'),
        ('cl', 'Cancelled')
    ], string='Status', default='dr' ,readonly=True)


    @api.onchange('payment_amount','commission','swipe_commission')
    def _onchange_payment_amount(self):
        if self.swipe_commission is False:
            self.commission_pay = self.payment_amount * self.commission / 100
            self.commission_paid = 0.0
            self.total_to_swipe = self.payment_amount
            self.amount_to_deposit = self.payment_amount
        else:
            self.commission_pay = self.payment_amount * self.commission / 100
            self.commission_paid = 0.0
            charge = self.commission_pay * self.commission /100
            self.total_to_swipe = self.payment_amount + charge + self.commission_pay
            self.amount_to_deposit = self.payment_amount
            self.commission_swiped = self.commission_pay


    @api.onchange('commission_paid','amount_to_deposit','total_to_swipe','swipe_commission')
    def _onchange_status(self):
        if self.payment_amount != 0:
            if self.commission_pay <= 0:
                self.state ='up'
                if self.amount_to_deposit <= 0:
                    self.state = 'fd'
                    if self.total_to_swipe <= 0:
                        self. state = 'fs'

            if self.swipe_commission:
                self.state = 'up'
                if self.amount_to_deposit <= 0:
                    self.state = 'fd'
                    if self.total_to_swipe <= 0:
                        self.state = 'fs'






    @api.multi
    def rec_com(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Receive Commission',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'receive.commission.wizard',
            'target': 'new',
            'context': 'None'
        }


    @api.multi
    def dep_pay(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Deposit Payment',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'process.deposit.wizard',
            'target': 'new',
            'context': 'None'
        }



    @api.multi
    def swipe(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Swipe Card',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'swipe.card.wizard',
            'target': 'new',
            'context': 'None'
        }

    @api.multi
    def cancel_trans(self):
        if self.env['res.users'].has_group('account.group_account_manager'):
            for ccp in self.transaction_ref:

                trans_entry = ccp.id
                trans_master = self.env['trans.master'].search([('id','=',trans_entry)])
                trans_master.cancel_trans()


            for ccp in self.payment_ref:

                receipt_voucher = ccp.id
                receipt_master =self.env['receipt.voucher'].search([('id','=',receipt_voucher)])
                receipt_master.action_cancel()


            for ccp in self.deposit_ref:

                payment_voucher = ccp.id
                payment_master =self.env['payment.voucher'].search([('id','=',payment_voucher)])
                payment_master.action_cancel()
            self.write({'state': 'cl'})
        else:
            raise UserError(
                _('You can not cancel the entry,to delete this entry user should belong to the Advisor group'))

    @api.model
    def create(self, values):

        record = super(ccPayment, self).create(values)
        if self.serial is False:
            record.serial = self.env['ir.sequence'].next_by_code('cc.payment') or 'new'
        return record

    @api.multi
    def unlink(self):
        for ccp in self:
            if ccp.state != 'dr':
                raise UserError(_('You can not delete this transaction. Please Cancel and create a new document if required'))

        return super(ccPayment, self).unlink()


