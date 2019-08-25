{
    'name': 'Transaction Management',
    'version': '1.0',
    'category': 'Accounting',
    'sequence': 14,
    'author': "Chlpn",
    'website': 'https://www.chlpn.ae',
    'summary': '',
    'depends': ['account', 'account_accountant','account_cancel','web_readonly_bypass','base_multi_company'],
    'data': [
                'views/trans_security.xml',
                'views/machine_bank_view.xml',
                'views/credit_card_payment_view.xml',
                'views/all_wizard_view.xml',
                'views/machine_master_view.xml',
                'views/inter_company.xml',
                'views/transaction_management_view.xml',
                'views/payment_voucher.xml',
                'views/receipt_voucher.xml',
                'views/branch_view.xml',
                'views/merchant_transfer.xml',
                'data/masters.xml',
                'security/ir.model.access.csv',
                'reports/report.xml',
                'reports/invoice_report.xml',
                'dynamic/daily_report_view.xml',
                'dynamic/report_daily_summary_template.xml',
                'views/card_bank_view.xml',
                'dynamic/running_capital_template.xml'


            ],
    'demo': [

            ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
