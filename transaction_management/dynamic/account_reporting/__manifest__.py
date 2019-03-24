{
    'name': 'account reporting',
    'version': '1.0',
    'category': 'Accounting &amp; Finance',
    'sequence': 14,
    'author': "iSquare Informatics",
    'website': 'https://www.isi.ae',
    'summary': '',
    'depends': ['account','account_accountant','mail', 'report','base'],
    'data': [
              'report/ledger_rpt.xml',
              'report/cheque_report.xml',
              'report/statement_customer.xml',
              'report/statement_vendor.xml',
              'wizard/custom_ledger_view.xml',
              'wizard/custom_statement_customer.xml',
              'wizard/custom_statement_vendor.xml'
               
               
               
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
