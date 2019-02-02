# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class TransMaster(models.Model):
    _name = "trans.master"
    _description = "Transaction Management"
    _rec_name = 'transaction_no'

    company_id = fields.Many2one(
        'res.company',
        'Company',
        default=lambda self: self.env.user.company_id
    )
    transaction_no = fields.Char(string='Transaction Number')
    transaction_date = fields.Date(string='Date',default=fields.Date.context_today, required=True)
    transaction_amount = fields.Float(string='Amount',)
    commission_included = fields.Boolean(string='Include Commission')
    amount_to_swipe = fields.Float(string='Amount to Swipe',store=True)
    amount_to_customer = fields.Float(string='Amount to customer',store=True)
    commission = fields.Float(string='Commission')
    cost_to_commission = fields.Float(string='Cost of Commission')
    margin = fields.Float(string='margin')
    cash_paid_customer = fields.Float(string='Cash Paid')
    balance = fields.Float(string='Balance')
    machine_name = fields.Many2one('machine.master', ondelete='restrict')
    sales_percentage = fields.Float(string='Sales Percentage')
    cost_percentage = fields.Float(string='Cost Percentage')
    customer = fields.Many2one('res.partner', string="Customer", ondelete='restrict')
    customer_mobile = fields.Char(related='customer.mobile',string='Mobile')
    journal_ref = fields.Many2one('account.move', string="Accounting Reference")
    customer_balance =fields.Char(string="Customer Balance", store=True, readonly="True")
    machine_balance = fields.Float(string="Machine Balance", readonly="True")
    cash_balance = fields.Float(string="Cash Balance")


    note = fields.Text(string="Notes")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft',readonly=True)

    @api.onchange('machine_name')
    def _onchange_machine_name(self):
        self.sales_percentage = self.machine_name.sales_percentage
        self.cost_percentage =self.machine_name.cost_percentage

    @api.onchange('customer')
    def _compute_cbal(self):
        account = self.customer.property_account_receivable_id.id
        customer = self.customer.id
        self.env.cr.execute(
            """select sum(debit-credit) from account_move_line left join account_move on account_move_line.move_id=account_move.id where account_id=%s and account_move_line.partner_id=%s and  account_move.state='posted' group by account_id""",(account,customer))
        self.customer_balance = self.env.cr.fetchall()[0(0)]





    @api.onchange('transaction_amount','commission_included','sales_percentage')
    def _onchange_amount_to_customer(self):
        #if not self.machine_name:
            #raise UserError(_('Please select the Machine Name'))
        #else:
        if self.commission_included == False:
            self.amount_to_customer = self.transaction_amount
            self.amount_to_swipe = (self.amount_to_customer * 100 / (100 - self.sales_percentage))
            self.commission = self.amount_to_swipe - self.amount_to_customer
            self.cost_to_commission = (self.amount_to_swipe * self.cost_percentage / 100)
            self.cash_paid_customer = self.amount_to_customer
            self.balance = self.amount_to_customer - self.cash_paid_customer
            self.margin = self.commission - self.cost_to_commission
        else:
            self.amount_to_swipe = self.transaction_amount
            self.commission = (self.amount_to_swipe * self.sales_percentage / 100)
            self.amount_to_customer = (self.amount_to_swipe - self.commission)
            self.cost_to_commission = (self.amount_to_swipe * self.cost_percentage / 100)
            self.cash_paid_customer = self.amount_to_customer
            self.balance = self.amount_to_customer - self.cash_paid_customer
            self.margin = self.commission - self.cost_to_commission

    @api.onchange('cash_paid_customer')
    def _cash_paid_customer(self):
        self.balance = self.amount_to_customer - self.cash_paid_customer

    @api.multi
    def post(self):
        if self.transaction_no is False:
            self.transaction_no = self.env['ir.sequence'].next_by_code('trans.master') or 'new'
        ir_model_obj = self.env['ir.model.data']
        model, journal_id = ir_model_obj.get_object_reference('transaction_management', 'transaction_journal')
        if self.machine_name.rented is True :
            if self.balance > 0:
                line_ids = [
                    (0, 0,
                     {'journal_id': journal_id, 'account_id': self.machine_name.rented_from.property_account_receivable_id.id,
                      'name': self.machine_name.name + "/" + self.transaction_no,'partner_id': self.machine_name.rented_from.id,
                      'amount_currency': 0.0, 'debit': self.amount_to_swipe - self.cost_to_commission}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.machine_name.cost_ac.id, 'name':self.machine_name.name + "/" + self.transaction_no,
                            'amount_currency': 0.0, 'debit': self.cost_to_commission}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.machine_name.cash_ac.id,
                            'name':self.machine_name.name + "/" + self.transaction_no,
                            'amount_currency': 0.0, 'credit': self.cash_paid_customer}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.machine_name.income_ac.id,
                            'name': self.machine_name.name + "/" + self.transaction_no,
                            'amount_currency': 0.0, 'credit': self.commission}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.customer.property_account_receivable_id.id,
                            'name': self.machine_name.name + "/" + self.transaction_no,'partner_id': self.customer.id,
                            'amount_currency': 0.0, 'credit': self.balance})

                ]
            elif self.balance < 0:
                line_ids = [
                    (0, 0,
                     {'journal_id': journal_id,
                      'account_id': self.machine_name.rented_from.property_account_receivable_id.id,
                      'name': self.machine_name.name + "/" + self.transaction_no,
                      'partner_id': self.machine_name.rented_from.id,
                      'amount_currency': 0.0, 'debit': self.amount_to_swipe - self.cost_to_commission}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.machine_name.cost_ac.id,
                            'name': self.machine_name.name + "/" + self.transaction_no,
                            'amount_currency': 0.0, 'debit': self.cost_to_commission}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.machine_name.cash_ac.id,
                            'name': self.machine_name.name + "/" + self.transaction_no,
                            'amount_currency': 0.0, 'credit': self.cash_paid_customer}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.machine_name.income_ac.id,
                            'name': self.machine_name.name + "/" + self.transaction_no,
                            'amount_currency': 0.0, 'credit': self.commission}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.customer.property_account_receivable_id.id,
                            'name': self.machine_name.name + "/" + self.transaction_no, 'partner_id': self.customer.id,
                            'amount_currency': 0.0, 'debit': abs(self.balance)})

                ]
            else :
                line_ids = [
                    (0, 0,
                     {'journal_id': journal_id,
                      'account_id': self.machine_name.rented_from.property_account_receivable_id.id,
                      'name': self.machine_name.name + "/" + self.transaction_no,
                      'partner_id': self.machine_name.rented_from.id,
                      'amount_currency': 0.0, 'debit': self.amount_to_swipe - self.cost_to_commission}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.machine_name.cost_ac.id,
                            'name': self.machine_name.name + "/" + self.transaction_no,
                            'amount_currency': 0.0, 'debit': self.cost_to_commission}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.machine_name.cash_ac.id,
                            'name': self.machine_name.name + "/" + self.transaction_no,
                            'amount_currency': 0.0, 'credit': self.cash_paid_customer}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.machine_name.income_ac.id,
                            'name': self.machine_name.name + "/" + self.transaction_no,
                            'amount_currency': 0.0, 'credit': self.commission}),

                ]
        else :
            if self.balance > 0:
                line_ids = [
                    (0, 0,
                     {'journal_id': journal_id, 'account_id': self.machine_name.merchant_bank_ac.id,
                      'name': self.machine_name.name + "/" + self.transaction_no,'partner_id': self.machine_name.rented_from.id,
                      'amount_currency': 0.0, 'debit': self.amount_to_swipe - self.cost_to_commission}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.machine_name.cost_ac.id, 'name':self.machine_name.name + "/" + self.transaction_no,
                            'amount_currency': 0.0, 'debit': self.cost_to_commission}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.machine_name.cash_ac.id,
                            'name':self.machine_name.name + "/" + self.transaction_no,
                            'amount_currency': 0.0, 'credit': self.cash_paid_customer}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.machine_name.income_ac.id,
                            'name': self.machine_name.name + "/" + self.transaction_no,
                            'amount_currency': 0.0, 'credit': self.commission}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.customer.property_account_receivable_id.id,
                            'name': self.machine_name.name + "/" + self.transaction_no,'partner_id': self.customer.id,
                            'amount_currency': 0.0, 'credit': self.balance})

                ]
            elif self.balance < 0:
                line_ids = [
                    (0, 0,
                     {'journal_id': journal_id,
                      'account_id': self.machine_name.merchant_bank_ac.id,
                      'name': self.machine_name.name + "/" + self.transaction_no,
                      'partner_id': self.machine_name.rented_from.id,
                      'amount_currency': 0.0, 'debit': self.amount_to_swipe - self.cost_to_commission}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.machine_name.cost_ac.id,
                            'name': self.machine_name.name + "/" + self.transaction_no,
                            'amount_currency': 0.0, 'debit': self.cost_to_commission}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.machine_name.cash_ac.id,
                            'name': self.machine_name.name + "/" + self.transaction_no,
                            'amount_currency': 0.0, 'credit': self.cash_paid_customer}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.machine_name.income_ac.id,
                            'name': self.machine_name.name + "/" + self.transaction_no,
                            'amount_currency': 0.0, 'credit': self.commission}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.customer.property_account_receivable_id.id,
                            'name': self.machine_name.name + "/" + self.transaction_no, 'partner_id': self.customer.id,
                            'amount_currency': 0.0, 'debit': abs(self.balance)})

                ]
            else :
                line_ids = [
                    (0, 0,
                     {'journal_id': journal_id,
                      'account_id': self.machine_name.merchant_bank_ac.id,
                      'name': self.machine_name.name + "/" + self.transaction_no,
                      'partner_id': self.machine_name.rented_from.id,
                      'amount_currency': 0.0, 'debit': self.amount_to_swipe - self.cost_to_commission}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.machine_name.cost_ac.id,
                            'name': self.machine_name.name + "/" + self.transaction_no,
                            'amount_currency': 0.0, 'debit': self.cost_to_commission}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.machine_name.cash_ac.id,
                            'name': self.machine_name.name + "/" + self.transaction_no,
                            'amount_currency': 0.0, 'credit': self.cash_paid_customer}),
                    (0, 0, {'journal_id': journal_id, 'account_id': self.machine_name.income_ac.id,
                            'name': self.machine_name.name + "/" + self.transaction_no,
                            'amount_currency': 0.0, 'credit': self.commission}),

                ]

        vals = {
            'journal_id': journal_id,
            'ref': self.machine_name.name + "/" + self.transaction_no,
            'date': self.transaction_date,
            'line_ids': line_ids,
        }
        account_move = self.env['account.move'].create(vals)
        account_move.post()
        self.journal_ref = account_move.id
        self.state = 'posted'

    @api.model
    def create(self,values):

        record = super(TransMaster, self).create(values)
        record.post()
        return record

    #@api.multi
    #def write(self, values):

        #record = super(TransMaster, self).write(values)
        #record.post()
        #return record

    @api.multi
    def unlink(self):
        for trans in self:
            if trans.state == 'posted' :
                raise UserError(_('You can not delete posted Transaction.'))
            if not trans.transaction_no is False :
                raise UserError(_('You can not delete posted or cancelled Transaction.'))

        return super(TransMaster, self).unlink()


    @api.multi
    def action_cancel(self):
        if self.env['res.users'].has_group('account.group_account_manager'):
            account_entry = self.journal_ref.id
            journal_entry = self.env['account.move'].search([('id', '=', account_entry)])
            if len(journal_entry):
                journal_entry.button_cancel()
                journal_entry.unlink()
                self.write({'state': 'cancelled'})
        else:
            raise UserError(
                _('You can not cancel the entry,to delete this entry user should belong to the Advisor group'))

    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})



    @api.constrains('amount_to_swipe','amount_to_customer','sales_percentage')
    def _check_something(self):
        for record in self:
            if record.amount_to_swipe <= 0:
                raise ValueError("Value of Amount to swipe must be greater than Zero")
            if record.amount_to_customer <= 0:
                raise ValueError("Value of Amount to Customer must be greater than Zero")
            if record.sales_percentage <= 0:
                raise ValueError("Value of Sales Percentage must be greater than Zero")