# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import amount_to_text_en



class MerchantTransfer(models.Model):
    _inherit = ["multi.company.abstract"]
    _name = "merchant.transfer"

    name = fields.Char(string='Name', size=64, readonly=True)
    transaction_date = fields.Date(string='Transaction Date', required=True, default=fields.Date.context_today)
    merchant_ac = fields.Many2one('account.account', string="Merchant Account", required=True, ondelete='restrict',
                              domain=lambda self: [
                                  ('user_type_id', '=', self.env.ref('account.data_account_type_credit_card').id)])
    linked_bank_ac = fields.Many2one('account.account', string="Linked Bank Account", required=True, ondelete='restrict',readonly=True,
                                  domain=lambda self: [
                                      ('user_type_id', '=', self.env.ref('account.data_account_type_liquidity').id)])

    journal_id = fields.Many2one('account.journal', string="Journal",  required=True, readonly=True)

    description = fields.Char(string='Description')
    amount = fields.Float('Transferred Amount', required=True)
    account_move_id = fields.Many2one('account.move', string="Accounting Entry", readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('post', 'Post'),
        ('cancel', 'Cancelled'),
    ], string='Status', default='draft', readonly=True)
    _sql_constraints = [('name_uniq', 'unique (name)', 'Transaction Number must be unique !')]
    _defaults = {'name': lambda self, cr, uid, context: 'Transaction'}

    @api.onchange('merchant_ac')
    def _onchange_merchant(self):
        ir_model_obj = self.env['ir.model.data']
        model, rjournal_id = ir_model_obj.get_object_reference('transaction_management', 'merchant_journal')
        self.journal_id = rjournal_id
        if self.merchant_ac:
            self.env.cr.execute(
            """select linked_bank_ac from machine_master where merchant_bank_ac=%s and  linked_bank_ac is not NULL LIMIT 1""", (self.merchant_ac.id,))

            value = self.env.cr.fetchone()

            if type(value[0]) is int:
                self.linked_bank_ac = value[0]
            else:
                self.linked_bank_ac = 0


    @api.multi
    def unlink(self):
        for transaction in self:
            if transaction.state == 'post':
                raise UserError(_('You can not delete posted transaction, kindly cancel it or edit it by set to draft'))
            elif self.name :
                raise UserError(_('You can not delete a transaction once posted, kindly cancel it or edit it by set to draft'))

        return super(MerchantTransfer, self).unlink()

    @api.multi
    def action_draft(self):
             self.write({'state': 'draft'})

    @api.multi
    def action_cancel(self):
        if self.env['res.users'].has_group('account.group_account_manager'):
            account_entry = self.account_move_id.id

            journal_entry = self.env['account.move'].search([('id', '=', account_entry)])
            if len(journal_entry):
                journal_entry.button_cancel()
                journal_entry.unlink()

            self.write({'state': 'cancel'})

        else:
            raise UserError(_('You can not cancel the entry,to delete this entry user should belong to the Advisor group'))
            

    @api.multi
    def post(self):
        merchant_transfer = self.env['ir.sequence'].next_by_code('merchant.transfer') or 'new'
        self.write({'name': merchant_transfer})

        if self.description:
            desc = self.description + ' /' + self.name
        line_ids = [
            (0, 0,
             {'journal_id': self.journal_id.id, 'account_id': self.linked_bank_ac.id,
              'name': desc,
              'amount_currency': 0.0, 'debit': self.amount}),
            (0, 0, {'journal_id': self.journal_id.id, 'account_id': self.merchant_ac.id,
                    'name': desc, 'amount_currency': 0.0, 'credit': self.amount,
                    })
        ]
        vals = {
            'journal_id': self.journal_id.id,
            'ref': merchant_transfer,
            'narration': desc,
            'date': self.transaction_date,
            'line_ids': line_ids,
        }
        account_move = self.env['account.move'].create(vals)
        account_move.post()

        self.write({'state': 'post', 'account_move_id': account_move.id})
