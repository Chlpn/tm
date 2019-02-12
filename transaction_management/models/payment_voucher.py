# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import amount_to_text_en

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    cash_journal = fields.Boolean('Cash Journal ?')


class PaymentVoucher(models.Model):
    _inherit = ["multi.company.abstract"]
    _name = "payment.voucher"

    name = fields.Char(string='Name', size=64, readonly=True)
    journal_id = fields.Many2one('account.journal', string="Journal", domain=[('cash_journal', '=', True)], required=True)
    transaction_date = fields.Date(string='Transaction Date', required=True, default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string="Paid To", required=True)
    commercial_partner_id = fields.Many2one('res.partner', string='Commercial Entity', compute_sudo=True,
                                            related='partner_id.commercial_partner_id', store=True, readonly=True,
                                            help="The commercial entity that will be used on Journal Entries for this invoice")
    account_id = fields.Many2one('account.account', string="Account", required=True)
    description = fields.Char(string='Description')
    received_by = fields.Char(string='Payment Received By')
    designation = fields.Char(string='Receiver Designation')
    phone = fields.Char(string='Receiver Mobile No.')
    amount = fields.Float('Amount', required=True)
    account_move_id = fields.Many2one('account.move', string="Accounting Entry", readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('post', 'Post'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', readonly=True)
    _sql_constraints = [('name_uniq', 'unique (name)', 'Cash payment voucher must be unique !')]
    _defaults = {'name': lambda self, cr, uid, context: 'Payment'}

    @api.onchange('partner_id')
    def _onchange_partner(self):

        if self.partner_id.is_company:
            comp = self.partner_id.company_id.id
            ccomp = self.env.user.company_id.id
            recs = self.env['inter.company']
            for rec in recs:
                if recs.company_id == ccomp & recs.related_company_id == comp:
                    self.account_id = recs.related_ac



        elif self.partner_id.supplier:
            self.account_id = self.partner_id.property_account_payable_id
        elif self.partner_id.customer:
            self.account_id = self.partner_id.property_account_receivable_id

    @api.multi
    def unlink(self):
        for voucher in self:
            if voucher.state == 'post':
                raise UserError(_('You can not delete posted vouchers.'))
        return super(PaymentVoucher, self).unlink()

    @api.multi
    def print_cash(self):
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'advanced_accounting.cash_payment_report'
        }

    @api.multi
    def amount_to_text(self, amount, currency='AED'):
        convert_amount_in_words = amount_to_text_en.amount_to_text(amount, lang='en', currency='')
        convert_amount_in_words = convert_amount_in_words.replace(' and Zero Cent', ' Only ')
        return convert_amount_in_words
   #changes in py done by manali     
    @api.multi
    def action_cancel(self):
        if self.env['res.users'].has_group('account.group_account_manager'):
            account_entry = self.account_move_id.id
    #        self.write({'account_move_id': False})
            journal_entry = self.env['account.move'].search([('id', '=', account_entry)])
            if len(journal_entry):
                journal_entry.button_cancel()
                journal_entry.unlink()
                self.write({'state': 'cancel'})
        else:
            raise UserError(_('You can not cancel the entry,to delete this entry user should belong to the Advisor group'))
            

    @api.multi
    def post(self):
        voucher_name = self.env['ir.sequence'].next_by_code('payment.voucher') or 'new'
        if not self.journal_id.cash_journal:
            raise UserError(_('Selected journal is not a Cash Journal.'))
        description = ""
        if self.description:
            description = self.description
        line_ids = [
            (0, 0,
             {'journal_id': self.journal_id.id, 'account_id': self.account_id.id,
              'name': description, 'partner_id': self.commercial_partner_id.id,
              'amount_currency': 0.0, 'debit': self.amount}),
            (0, 0, {'journal_id': self.journal_id.id, 'account_id': self.journal_id.default_credit_account_id.id,
                    'name': description, 'amount_currency': 0.0, 'credit': self.amount,
                    })
        ]
        vals = {
            'journal_id': self.journal_id.id,
            'ref': voucher_name,
            'narration': description,
            'date': self.transaction_date,
            'line_ids': line_ids,
        }
        account_move = self.env['account.move'].create(vals)
        account_move.post()
        self.write({'state': 'post', 'name': voucher_name, 'account_move_id': account_move.id})
