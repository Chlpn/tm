# -*- coding: utf-8 -*-

from odoo import fields, models, api


class InterCompany(models.Model):
    _name = "inter.company"
    _rec_name = "company_id"

    company_id =fields.Many2one('res.company', string="Branch", required=True, ondelete='restrict')
    related_company_id =fields.Many2one('res.company', string="Related Branch", required=True, ondelete='restrict')
    _sql_constraints = [('company_ids_uniq', 'UNIQUE (company_id,related_company_id)', 'related account already exist for this company!')]

    related_ac = fields.Many2one('account.account', string="Inter Company Account", required=True, ondelete='restrict')

