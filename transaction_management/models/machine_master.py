# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MachineMaster(models.Model):
    _name = "machine.master"
    _description = "Machine Master"

    active = fields.Boolean(string="Active", default=1)
    company_id = fields.Many2one('res.company', string="company", required=True, ondelete='restrict')
    branch = fields.Many2one('company.branch', string ="Branch")
    name = fields.Char(string='Machine Name')
    rent_again = fields.Boolean(string='Rent to Branch')
    parent_name = fields.Many2one('machine.master',string='Parent Machine', ondelete='restrict')
    merchant_id = fields.Char(string='Merchant ID',)
    terminal_id = fields.Char(string='Terminal ID', )
    bank_name = fields.Many2one('machine.bank', string='Bank Name', ondelete='restrict')
    rented =fields.Boolean(string='is Machine Rented')
    rented_from = fields.Many2one('res.partner', string="Rented From", ondelete='restrict', domain=[('supplier', '=', '1')])
    sales_percentage = fields.Float(string='Default Sales Percentage')
    cost_percentage = fields.Float(string='Cost Percentage')
    merchant_bank_ac = fields.Many2one('account.account', string="Bank Account", ondelete='restrict')
    cost_ac = fields.Many2one('account.account', string="Cost Account",required=True, ondelete='restrict')
    income_ac = fields.Many2one('account.account', string="Income Account",required=True, ondelete='restrict')
    cash_ac = fields.Many2one('account.account', string="Cash Account",required=True, ondelete='restrict')

    @api.onchange('parent_name','branch')
    def _onchange_parent_name(self):
        self.cost_ac = self.branch.cost_ac.id
        self.income_ac = self.branch.income_ac.id
        self.cash_ac = self.branch.cash_ac.id
        if self.rent_again:
           if self.parent_name:

               comp = self.branch.company_id.id
               ccomp = self.parent_name.branch.company_id.id
               value = self.env['machine.master'].search([('parent_name', '=', self.parent_name.id)])
               if comp == ccomp:
                   raise UserError("You cannot rent to same branch")
               elif value :
                    raise UserError("Machine Already rented")
               else:
                    self.env.cr.execute(
                        """select related_ac from inter_company where company_id=%s and related_company_id=%s""", (ccomp, comp))
                    value = self.env.cr.fetchone()
               if value is None:
                    self.merchant_bank_ac = 0
               else:
                    self.merchant_bank_ac = value[0]

    @api.constrains('branch','parent_name')
    def _check_company(self):
        if self.branch.company_id.id == self.parent_name.branch.company_id.id:
            raise UserError("You cannot rent to same branch")