{
    'name': 'Transaction Management',
    'version': '1.0',
    'category': 'Accounting',
    'sequence': 14,
    'author': "iSquare Informatics",
    'website': 'https://www.isi.ae',
    'summary': '',
    'depends': ['account', 'account_accountant','account_cancel','web_readonly_bypass'],
    'data': [
                'views/customer_bank_view.xml','views/machine_master_view.xml','views/transaction_management_view.xml',
'views/transaction.xml'
            ],
    'demo': [

            ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
