# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class ChequeConfiguration(models.Model):
    _name = 'cheque.config.settings'
    _inherit = 'res.config.settings'

    email = fields.Char('Email', required=True)
    alert_inbound = fields.Integer('For Inbound Cheques', required=True, default=1)
    alert_outbound = fields.Integer('For Outbound Cheques', required=True, default=1)
    interim_account_id = fields.Many2one('account.account', string="Customer Cheque Interim Account", required=True)
    charges_account_id = fields.Many2one('account.account', string="Bank Charges Account", required=True)

    @api.model
    def get_default_charges_account_id(self, fields):
        last_ids = self.env['cheque.config.settings'].sudo().search([], order='id desc', limit=1)
        charges_account_id = last_ids.charges_account_id.id
        return {'charges_account_id': charges_account_id}

    @api.model
    def get_default_interim_account_id(self, fields):
        last_ids = self.env['cheque.config.settings'].sudo().search([], order='id desc', limit=1)
        interim_account_id = last_ids.interim_account_id.id
        return {'interim_account_id': interim_account_id}\

    @api.model
    def get_default_email(self, fields):
        last_ids = self.env['cheque.config.settings'].sudo().search([], order='id desc', limit=1)
        email = last_ids.email
        return {'email': email}\

    @api.model
    def get_default_alert_inbound(self, fields):
        last_ids = self.env['cheque.config.settings'].sudo().search([], order='id desc', limit=1)
        alert_inbound = last_ids.alert_inbound
        return {'alert_inbound': alert_inbound}\

    @api.model
    def get_default_alert_outbound(self, fields):
        last_ids = self.env['cheque.config.settings'].sudo().search([], order='id desc', limit=1)
        alert_outbound = last_ids.alert_outbound
        return {'alert_outbound': alert_outbound}


    @api.multi
    def execute(self):
        self.ensure_one()
        if not self.env['res.users'].has_group('cheque_management.group_cheque_admin'):
            
     
            if not self.env.user._is_superuser() and not self.env.user.has_group('base.group_system'):
                raise AccessError(_("Only administrators can change the settings"))

        self = self.with_context(active_test=False)
        classified = self._get_classified_fields()

        # default values fields
        IrValues = self.env['ir.values'].sudo()
        for name, model, field in classified['default']:
            IrValues.set_default(model, field, self[name])

        # group fields: modify group / implied groups
        for name, groups, implied_group in classified['group']:
            if self[name]:
                groups.write({'implied_ids': [(4, implied_group.id)]})
            else:
                groups.write({'implied_ids': [(3, implied_group.id)]})
                implied_group.write({'users': [(3, user.id) for user in groups.mapped('users')]})

        # other fields: execute all methods that start with 'set_'
        for method in dir(self):
            if method.startswith('set_'):
                getattr(self, method)()

        # module fields: install/uninstall the selected modules
        to_install = []
        to_uninstall_modules = self.env['ir.module.module']
        lm = len('module_')
        for name, module in classified['module']:
            if self[name]:
                to_install.append((name[lm:], module))
            else:
                if module and module.state in ('installed', 'to upgrade'):
                    to_uninstall_modules += module

        if to_uninstall_modules:
            to_uninstall_modules.button_immediate_uninstall()

        action = self._install_modules(to_install)
        if action:
            return action

        if to_install or to_uninstall_modules:
            # After the uninstall/install calls, the registry and environments
            # are no longer valid. So we reset the environment.
            self.env.reset()
            self = self.env()[self._name]
        config = self.env['res.config'].next() or {}
        if config.get('type') not in ('ir.actions.act_window_close',):
            return config

        # force client-side reload (update user menu and current view)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

