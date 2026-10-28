{
    'name': 'FlousFlow Community Accounting Suite',
    'version': '20.0.1.33.0',
    'category': 'Accounting',
    'summary': 'Annual Report, Bank Reconciliation Statement, Accounting Reports, '
               'Asset Management and Budget, Recurring Payments, '
               'Lock Dates, Fiscal Year, Period Closing, Accounting Dashboard, Financial Reports, '
               'Cash Flow Statement, Cash Forecast, Customer Follow up Management, Bank Reconciliation, '
               'Cheque Printing, Automatic Currency Rates, Currency Revaluation, Bank Statement Import, '
               'Vendor Bill OCR, Working File Balance Review',
    'description': 'Odoo 20 Financial Reports, Asset Management and '
                   'Budget, Financial Reports, Cash Flow Statement, Cash Forecast, '
                   'Recurring Payments, Bank Reconciliation, Customer Follow Up Management, '
                   'Account Lock Date, Fiscal Year and Period Closing, Cheque Printing, '
                   'Automatic Currency Rates, Accounting Dashboard, Vendor Bill OCR, '
                   'Working File Audit Checklist and Comparative Account Balances',
    'live_test_url': 'https://www.youtube.com/c/OdooMates',
    'sequence': '1',
    'author': 'FlousFlow (based on Odoo Community modules)',
    'maintainer': 'FlousFlow',
    'license': 'LGPL-3',
    'support': 'support@flousflow.com',
    'depends': [
        'accounting_pdf_reports',
        'sale_stock',
        'purchase_stock',
        'om_account_asset',
        'om_account_budget',
        'om_fiscal_year',
        'om_recurring_payments',
        'om_account_daily_reports',
        'om_account_followup',
        'om_account_reconcile',
        'om_account_cash_forecast',
        'om_account_check_printing',
        'om_currency_rate_update',
        'om_currency_revaluation',
        'om_account_bank_statement_import',
        'om_account_bill_ocr',
        'om_spreadsheet_account',
        'spreadsheet',
        'om_spreadsheet_account_asset',
        'om_spreadsheet_account_budget',
        'om_spreadsheet_account_followup',
        'ff_account_transfer',
        'flousflow_branch_analytic',
    ],
    'assets': {
        'web.assets_backend': [
            'om_account_accountant/static/src/review_accrual/review_accrual_list.js',
            'om_account_accountant/static/src/review_accrual/review_accrual_list.xml',
            'om_account_accountant/static/src/journal_audit/journal_audit.js',
            'om_account_accountant/static/src/journal_audit/journal_audit.xml',
            'om_account_accountant/static/src/journal_audit/journal_audit.scss',
            'om_account_accountant/static/src/deferred_schedule/deferred_schedule.js',
            'om_account_accountant/static/src/deferred_schedule/deferred_schedule.xml',
            'om_account_accountant/static/src/deferred_schedule/deferred_schedule.scss',
            'om_account_accountant/static/src/working_file_spreadsheet/working_file_spreadsheet_loader.js',
            'om_account_accountant/static/src/working_file_spreadsheet/working_file_spreadsheet_loader.xml',
            'om_account_accountant/static/src/working_file_spreadsheet/working_file_spreadsheet_field.js',
            'om_account_accountant/static/src/working_file_spreadsheet/working_file_spreadsheet_field.xml',
            'om_account_accountant/static/src/working_file_spreadsheet/working_file_spreadsheet.scss',
            'om_account_accountant/static/src/working_file_balance/working_file_balance.js',
            'om_account_accountant/static/src/working_file_balance/working_file_balance.xml',
        ],
        'spreadsheet.o_spreadsheet': [
            'om_account_accountant/static/src/working_file_spreadsheet/working_file_spreadsheet.js',
            'om_account_accountant/static/src/working_file_spreadsheet/working_file_spreadsheet.xml',
        ],
        'web.assets_tests': [
            'om_account_accountant/static/tests/tours/review_accrual_date_picker.js',
            'om_account_accountant/static/tests/tours/journal_audit_period_filter.js',
            'om_account_accountant/static/tests/tours/deferred_schedule_periods.js',
            'om_account_accountant/static/tests/tours/working_file_spreadsheet.js',
        ],
    },
    'data': [
        'security/group.xml',
        'security/ir.access.csv',
        'data/working_file_template.xml',
        'data/working_file_enterprise_templates.xml',
        'views/working_file_views.xml',
        'views/menu.xml',
        'views/review_menu.xml',
        'views/account_move_line_search.xml',
        'views/settings.xml',
        'views/account_tag.xml',
        'views/res_partner.xml',
        'views/account_bank_statement.xml',
        'views/payment_method.xml',
        'views/reconciliation.xml',
        'views/account_journal.xml',
    ],
    'application': True,
    'images': ['static/description/banner.gif'],
}

