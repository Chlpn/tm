# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp
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
    transaction_amount = fields.Float(string='Amount', digits=dp.get_precision('Account'))
    commission_included = fields.Boolean(string='Include Commission',default=True)
    amount_to_swipe = fields.Float(string='Amount to Swipe',store=True, digits=dp.get_precision('Account'))
    amount_to_customer = fields.Float(string='Amount to customer',store=True, digits=dp.get_precision('Account'))
    commission = fields.Float(string='Commission', digits=dp.get_precision('Account'))
    cost_to_commission = fields.Float(string='Cost of Commission', digits=dp.get_precision('Account'))
    cost_to_parent = fields.Float(string='Cost of Parent', digits=dp.get_precision('Account'))
    margin = fields.Float(string='margin', digits=dp.get_precision('Account'))
    cash_paid_customer = fields.Float(string='Cash Paid', digits=dp.get_precision('Account'))
    balance = fields.Float(string='Balance', digits=dp.get_precision('Account'))
    machine_name = fields.Many2one('machine.master', ondelete='restrict')
    sales_percentage = fields.Float(string='Sales Percentage', digits=dp.get_precision('Account'))
    cost_percentage = fields.Float(string='Cost Percentage', digits=dp.get_precision('Account'))
    parent_percentage = fields.Float(string='Parent Cost Percentage', digits=dp.get_precision('Account'))
    customer = fields.Many2one('res.partner', string="Customer", ondelete='restrict', domain=[('customer', '=', '1')])
    customer_mobile = fields.Char(related='customer.mobile',string='Mobile')
    journal_ref = fields.Many2one('account.move', string="Accounting Reference")
    rentagain_journal_ref = fields.Many2one('account.move', string="Accounting Reference")
    customer_balance =fields.Float(string="Customer Balance", store=True, readonly="True", compute="_compute_cbal", digits=dp.get_precision('Account'))
    machine_balance = fields.Float(string="Machine Balance", store=True,  readonly="True", compute="_compute_mbal", digits=dp.get_precision('Account'))
    cash_balance = fields.Float(string="Cash Balance", store=True,  readonly="True", compute="_compute_bal", digits=dp.get_precision('Account'))
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
        if self.machine_name.rent_again:
            self.parent_percentage = self.machine_name.parent_name.cost_percentage

    @api.depends('customer')
    def _compute_cbal(self):
        if self.customer :
            account = self.customer.property_account_receivable_id.id
            customer = self.customer.id
            self.env.cr.execute(
                """select sum(debit-credit) from account_move_line left join account_move on account_move_line.move_id=account_move.id where account_id=%s and account_move_line.partner_id=%s and  account_move.state='posted' group by account_id""",(account,customer))
            value = self.env.cr.fetchone()
            if value is None:
                self.customer_balance = 0
            else:
                self.customer_balance = value[0]


    @api.depends('machine_name')
    def _compute_mbal(self):
        if self.machine_name:

            if self.machine_name.rented is False:
                if self.machine_name.rent_again:
                    comp = self.machine_name.branch.company_id.id
                    ccomp = self.machine_name.parent_name.branch.company_id.id
                    self.env.cr.execute(
                        """select related_ac from inter_company where company_id=%s and related_company_id=%s""",
                        (comp, ccomp))
                    value = self.env.cr.fetchone()
                    if value is None:
                        account = 0
                    else:
                        account = value[0]
                else:

                    account = self.machine_name.merchant_bank_ac.id
                self.env.cr.execute(
                    """select sum(debit-credit) from account_move_line left join account_move on account_move_line.move_id=account_move.id where account_id=%s and  account_move.state='posted' group by account_id""",
                        (account,))

            else:
                account = self.machine_name.rented_from.property_account_payable_id.id
                customer = self.machine_name.rented_from.id
                self.env.cr.execute(
                    """select sum(debit-credit) from account_move_line left join account_move on account_move_line.move_id=account_move.id where account_id=%s and account_move_line.partner_id=%s and  account_move.state='posted' group by account_id""",
                    (account, customer))

            value = self.env.cr.fetchone()
            caccount = self.machine_name.branch.cash_ac.id
            self.env.cr.execute(
                """select sum(debit-credit) from account_move_line left join account_move on account_move_line.move_id=account_move.id where account_id=%s and  account_move.state='posted' group by account_id""",
                (caccount,))
            value2 = self.env.cr.fetchone()

            if value is None:
                self.machine_balance = 0
            else:
                self.machine_balance = -1 * value[0]

            if value2 is None:
                self.cash_balance = 0
            else:
                self.cash_balance = value2[0]


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
            if self.machine_name.rent_again:
                self.cost_to_parent = (self.amount_to_swipe * self.parent_percentage / 100)

        else:
            self.amount_to_swipe = self.transaction_amount
            self.commission = (self.amount_to_swipe * self.sales_percentage / 100)
            self.amount_to_customer = (self.amount_to_swipe - self.commission)
            self.cost_to_commission = (self.amount_to_swipe * self.cost_percentage / 100)
            self.cash_paid_customer = self.amount_to_customer
            self.balance = self.amount_to_customer - self.cash_paid_customer
            self.margin = self.commission - self.cost_to_commission
            if self.machine_name.rent_again:
                self.cost_to_parent = (self.amount_to_swipe * self.parent_percentage / 100)

    @api.onchange('cash_paid_customer')
    def _cash_paid_customer(self):
        self.balance = self.amount_to_customer - self.cash_paid_customer

    @api.multi
    def post(self):
        if self.transaction_no is False:
            self.transaction_no = self.env['ir.sequence'].next_by_code('trans.master') or 'new'

        journal_id = self.machine_name.branch.journal_id.id
        if self.machine_name.rented is True :
            post_account = self.machine_name.rented_from.property_account_payable_id.id
        else :
            post_account = self.machine_name.merchant_bank_ac.id

        if self.balance > 0:
            line_ids = [
                    (0, 0,
                     {'journal_id': journal_id, 'account_id': post_account,
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
                      'account_id': post_account,
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
                      'account_id': post_account,
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

        if self.machine_name.rent_again:
            rjournal_id = self.machine_name.parent_name.branch.journal_id.id
            comp = self.machine_name.branch.company_id.id
            ccomp = self.machine_name.parent_name.branch.company_id.id
            self.env.cr.execute(
                """select related_ac from inter_company where company_id=%s and related_company_id=%s""",
                (ccomp, comp))
            vvalue = self.env.cr.fetchone()
            if vvalue is None:
                paccount = 0
            
            paccount = vvalue[0]

            if self.machine_name.parent_name.rented:
                parent_account = self.machine_name.parent_name.rented_from.property_account_payable_id.id
            else:
                parent_account = self.machine_name.parent_name.merchant_bank_ac.id
            rline_ids = [
                (0, 0,
                 {'journal_id': rjournal_id,
                  'account_id': paccount,
                  'name': self.machine_name.name + "/" + self.transaction_no,
                  'partner_id': self.machine_name.branch.company_id.id,
                  'amount_currency': 0.0, 'credit': self.amount_to_swipe - self.cost_to_commission}),
                (0, 0,
                 {'journal_id': rjournal_id, 'account_id': self.machine_name.parent_name.branch.rentagain_income_ac.id,
                  'name': self.machine_name.name + "/" + self.transaction_no,
                  'amount_currency': 0.0, 'credit': self.cost_to_commission - self.cost_to_parent}),
                (0, 0, {'journal_id': rjournal_id, 'account_id': parent_account,
                        'name': self.machine_name.name + "/" + self.transaction_no,
                        'amount_currency': 0.0, 'debit': self.amount_to_swipe - self.cost_to_parent}),

            ]
            pvals = {
                'journal_id': rjournal_id,
                'ref': self.machine_name.name + "/" + self.transaction_no,
                'date': self.transaction_date,
                'line_ids': rline_ids,
            }
            raccount_move = self.env['account.move'].create(pvals)
            raccount_move.post()
            self.rentagain_journal_ref = raccount_move.id
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

            if self.machine_name.rent_again:
                raccount_entry = self.rentagain_journal_ref.id
                rjournal_entry = self.env['account.move'].search([('id', '=', raccount_entry)])
                if len(rjournal_entry):
                    rjournal_entry.button_cancel()
                    rjournal_entry.unlink()
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


class trans_ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        res = super(trans_ResPartner, self).name_search(name='', args=None, operator='ilike', limit=100)

        ids = self.search(args + ['|',('name', operator, name),('mobile', operator, name)], limit=limit)
        return ids.name_get()


