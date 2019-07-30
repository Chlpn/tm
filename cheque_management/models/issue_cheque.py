# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import amount_to_text_en
import logging

_logger = logging.getLogger(__name__)


class IssueCheque(models.Model):
    _name = "issue.cheque"

    cheque_id = fields.Many2one('cheque.master', string='Cheque Number', domain="[('state', '=', 'new')]",
                                required=True)
    date_issue = fields.Date(string='Print Date', default=fields.Date.context_today, required=True)
    cheque_date = fields.Date(string='Cheque Date', required=True)
    partner_id = fields.Many2one('res.partner', string="Issued To", required=True)
    commercial_partner_id = fields.Many2one('res.partner', string='Commercial Entity', compute_sudo=True,
                                            related='partner_id.commercial_partner_id', store=True, readonly=True,
                                            help="The commercial entity that will be used on Journal Entries for this invoice")

    name_in_cheque = fields.Char(string="Name in Cheque", required=True)
    issue_journal_entry = fields.Many2one('account.move', 'Accounting Entry', readonly=True)
    dest_account_id = fields.Many2one('account.account', string="Destination Account", required=True)
    amount = fields.Float('Amount', required=True)
    state = fields.Selection([
        ('new', 'New'),
        ('used', 'Used'),
        ('printed', 'Printed'),
    ], string='Status', readonly=True, default='new')

    @api.multi
    def copy(self):
        raise UserError(_('You cannot duplicate this record.'))

    @api.onchange('date_issue')
    def _onchange_date_issue(self):
        if self.date_issue and not self.cheque_date:
            self.cheque_date = self.date_issue

    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id:
            self.name_in_cheque = self.partner_id.name
            # print "kkkkkkkk", self.partner_id.name_get()

        if self.partner_id.supplier:
            self.dest_account_id = self.partner_id.property_account_payable_id
        elif self.partner_id.customer:
            self.dest_account_id = self.partner_id.property_account_receivable_id
        else:
            pass

    @api.model
    def create(self, vals):
        if vals['amount'] <= 0.01:
            raise UserError(_('Boss! you can issue a cheque with this amount :)'))
        self.env['cheque.master'].browse(vals['cheque_id']).write({'state': 'used',
                                                                   'partner_id': vals['partner_id'],
                                                                   'partner_account_id': vals['dest_account_id'],
                                                                   'date_issue': vals['date_issue'],
                                                                   'cheque_date': vals['cheque_date'],
                                                                   })
        vals['state'] = 'used'
        return super(IssueCheque, self).create(vals)

    @api.multi
    def post_cheque(self):
        ir_model_obj = self.env['ir.model.data']
        model, journal_id = ir_model_obj.get_object_reference('cheque_management', 'cheque_journal')
        line_ids = [
            (0, 0,
             {'journal_id': journal_id, 'account_id': self.cheque_id.bank_name.pdc_account_id.id,
              'name': self.cheque_id.name,
              'amount_currency': 0.0, 'credit': self.amount}),
            (0, 0, {'journal_id': journal_id, 'account_id': self.dest_account_id.id, 'name': '/',
                    'amount_currency': 0.0, 'debit': self.amount, 'partner_id': self.commercial_partner_id.id})
        ]
        vals = {
            'journal_id': journal_id,
            'ref': self.cheque_id.name,
            'date': self.date_issue,
            'line_ids': line_ids,
        }
        account_move = self.env['account.move'].create(vals)
        account_move.post()
        self.issue_journal_entry = account_move.id
        self.state = 'printed'
        self.cheque_id.write({'state': 'printed',
                              'date_issue': self.date_issue,
                              'cheque_date': self.cheque_date,
                              'account_move_ids': [(4, account_move.id)],
                              'partner_id': self.commercial_partner_id.id,
                              'partner_account_id': self.dest_account_id.id,
                              'amount': self.amount})

    @api.multi
    def print_cheque(self):
        print "printttt_chequeeeeee"
        pid = self.cheque_id.bank_name.paper_format_id.id
        #        reports = self.env['ir.action.report.xml']
        #        reports = reports.search([('name', '=', 'Cheque Print')])
        #        print'reports-=======================---',reports
        #        _logger.warning('=============================================== (%s).',reports)
        #
        #        if len(reports):
        self._cr.execute('UPDATE ir_act_report_xml ' \
                         'SET paperformat_id=%s ' \
                         'WHERE name=%s', (pid, 'Cheque Print',))
        #        reports.write({'paperformat_id':pid})
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'cheque_management.cheque_print_report'
        }

    @api.multi
    def amount_to_text(self, amount, currency='AED'):
        amount_to_text = amount_to_text_en.amount_to_text(amount, lang='en', currency='USD')
        amount_to_text = amount_to_text.replace(' and Zero Cent', ' Only')
        amount_to_text = amount_to_text.replace(' USD', '')
        amount_to_text = amount_to_text.replace(' Cents', ' fils Only')
        amount_to_text = amount_to_text.replace(' Cent', ' fils Only')

        return amount_to_text
