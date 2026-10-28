from odoo import Command
from odoo.tests import TransactionCase, new_test_user, tagged

# where each menu of the accounting apps stands: daily work, reports, settings
PARENTS = {
    'account.menu_action_account_moves_all': 'account.account_transactions_menu',
    'om_account_reconcile.menu_bank_reconciliation': 'om_account_reconcile.menu_reconciliation',
    'om_account_reconcile.menu_open_items_reconciliation': 'om_account_reconcile.menu_reconciliation',
    'om_account_reconcile.menu_move_line_match': 'om_account_reconcile.menu_reconciliation',
    'om_account_reconcile.menu_reconciliation': 'account.menu_finance_entries',
    'om_account_asset.menu_action_account_asset_asset_form': 'account.menu_finance_entries',
    'om_account_budget.menu_account_budget': 'account.menu_finance_entries',
    'om_recurring_payments.menu_recurring_payment': 'account.menu_finance_entries',
    'om_account_cash_forecast.menu_cash_forecast_item': 'account.menu_finance_entries',
    'om_fiscal_year.menu_action_change_lock_date': 'account.account_closing_menu',
    'accounting_pdf_reports.menu_account_report_bs': 'account.account_reports_legal_statements_menu',
    'accounting_pdf_reports.menu_account_report_pl': 'account.account_reports_legal_statements_menu',
    'accounting_pdf_reports.menu_account_report_cash_flow': 'account.account_reports_legal_statements_menu',
    'accounting_pdf_reports.menu_general_ledger': 'accounting_pdf_reports.menu_finance_reporting_ledgers',
    'accounting_pdf_reports.menu_general_balance_report': 'accounting_pdf_reports.menu_finance_reporting_ledgers',
    'accounting_pdf_reports.menu_finance_reporting_ledgers': 'account.menu_finance_reports',
    'accounting_pdf_reports.menu_finance_entries_accounting_ledgers': 'account.menu_finance_entries',
    'accounting_pdf_reports.menu_partner_ledger': 'account.account_reports_partners_reports_menu',
    'accounting_pdf_reports.menu_aged_trial_balance': 'account.account_reports_partners_reports_menu',
    'accounting_pdf_reports.menu_account_report': 'account.account_reports_taxes_and_fiscal_menu',
    'accounting_pdf_reports.menu_account_reports': 'account.account_account_menu',
    'om_account_asset.menu_asset_depreciation_schedule': 'account.account_reports_legal_statements_menu',
    'om_account_check_printing.menu_check_format': 'account.account_invoicing_menu',
    'om_account_followup.om_account_followup_menu': 'account.account_invoicing_menu',
    'om_account_asset.menu_action_account_asset_asset_list_normal_purchase':
        'om_account_accountant.menu_account_management_config',
    'om_account_budget.menu_account_budget_position': 'om_account_accountant.menu_account_management_config',
    'om_recurring_payments.menu_recurring_template': 'om_account_accountant.menu_account_management_config',
    'om_fiscal_year.menu_account_period_closing_task': 'om_account_accountant.menu_account_management_config',
}
# the folders replaced by the ones of the account module, or holding a single menu
REMOVED = (
    'accounting_pdf_reports.menu_finance_legal_statement',
    'accounting_pdf_reports.menu_finance_partner_reports',
    'accounting_pdf_reports.menu_finance_reports_settings',
    'om_account_asset.menu_finance_entries_assets',
    'om_account_followup.om_account_followup_main_menu',
    'om_recurring_payments.menu_recurring_payments',
    'om_account_accountant.menu_account_templates',
)


@tagged('post_install', '-at_install')
class TestMenus(TransactionCase):

    def test_menus_are_arranged(self):
        for xmlid, parent in PARENTS.items():
            with self.subTest(menu=xmlid):
                self.assertEqual(self.env.ref(xmlid).parent_id, self.env.ref(parent))
        for xmlid in REMOVED:
            self.assertFalse(self.env.ref(xmlid, raise_if_not_found=False), xmlid)

    def test_review_control_matches_enterprise_menu(self):
        control_menu = self.env.ref('account.account_audit_control_menu')
        actual = control_menu.child_id.filtered('active').sorted(
            key=lambda menu: (menu.sequence, menu.id)
        )
        expected = [
            self.env.ref('om_account_accountant.menu_review_journal_items'),
            self.env.ref('account.account_audit_trail_menu'),
            self.env.ref('om_account_accountant.menu_review_journal_audit'),
        ]
        self.assertEqual(actual.ids, [menu.id for menu in expected])
        self.assertEqual(
            self.env.ref('om_account_accountant.menu_review_moves_to_review').parent_id,
            self.env.ref('om_account_accountant.menu_review_work_queues'),
        )
        work_queues = self.env.ref('om_account_accountant.menu_review_work_queues')
        self.assertEqual(
            work_queues.child_id.filtered('active').sorted(key=lambda menu: (menu.sequence, menu.id)),
            self.env['ir.ui.menu'].browse([
                self.env.ref('om_account_accountant.menu_review_moves_to_review').id,
                self.env.ref('om_account_accountant.menu_review_moves_unposted').id,
            ]),
        )
        journal_items_action = self.env.ref('om_account_accountant.menu_review_journal_items').action
        self.assertEqual(journal_items_action, self.env.ref('account.action_account_moves_all'))
        self.assertEqual(journal_items_action.res_model, 'account.move.line')

    def test_review_menu_tree_matches_enterprise_destinations(self):
        expected_tree = {
            'account.account_audit_menu': [
                'account.account_audit_control_menu',
                'om_account_accountant.menu_review_audit',
                'om_account_accountant.menu_review_inventory_valuation',
                'om_account_accountant.menu_review_regularization',
                'om_account_accountant.menu_review_purchases',
                'om_account_accountant.menu_review_sales',
            ],
            'om_account_accountant.menu_review_audit': [
                'om_account_accountant.menu_review_working_files',
                'accounting_pdf_reports.menu_account_report_annual',
            ],
            'om_account_accountant.menu_review_regularization': [
                'om_account_accountant.menu_review_unrealized_currencies',
                'om_account_accountant.menu_review_deferred_revenues',
                'om_account_accountant.menu_review_deferred_expenses',
            ],
            'om_account_accountant.menu_review_purchases': [
                'om_account_accountant.menu_review_bill_to_receive',
                'om_account_accountant.menu_review_billed_not_received',
            ],
            'om_account_accountant.menu_review_sales': [
                'om_account_accountant.menu_review_invoice_to_be_issued',
                'om_account_accountant.menu_review_invoiced_not_delivered',
            ],
        }
        for parent_xmlid, child_xmlids in expected_tree.items():
            with self.subTest(menu=parent_xmlid):
                actual = self.env.ref(parent_xmlid).child_id.filtered('active').sorted(
                    key=lambda menu: (menu.sequence, menu.id)
                )
                expected_ids = [self.env.ref(xmlid).id for xmlid in child_xmlids]
                self.assertEqual(actual.ids, expected_ids)
        self.assertFalse(self.env.ref('om_account_accountant.menu_review_inventory').active)

    def test_no_two_menus_share_a_place(self):
        """ Menus with the same sequence under the same parent come in no given order. """
        roots = self.env.ref('account.menu_finance')
        menus = self.env['ir.ui.menu'].search([('id', 'child_of', roots.ids)])
        ours = self.env['ir.model.data'].search([
            ('model', '=', 'ir.ui.menu'), ('res_id', 'in', menus.ids), ('module', '!=', 'account'),
        ])
        for menu in self.env['ir.ui.menu'].browse(ours.mapped('res_id')):
            clashes = menu.parent_id.child_id.filtered(lambda other: other != menu and other.sequence == menu.sequence)
            self.assertFalse(clashes, '%s shares its place with %s' % (menu.complete_name, clashes.mapped('name')))

    def test_accountant_sees_the_daily_work(self):
        accountant = new_test_user(
            self.env, login='menu_accountant', groups='account.group_account_user',
            company_id=self.env.company.id, company_ids=[Command.set(self.env.company.ids)])
        visible = self.env['ir.ui.menu'].with_user(accountant)._visible_menu_ids()
        for xmlid in ('om_account_reconcile.menu_bank_reconciliation',
                      'om_account_reconcile.menu_open_items_reconciliation',
                      'om_account_reconcile.menu_move_line_match',
                      'om_account_budget.menu_account_budget',
                      'om_recurring_payments.menu_recurring_payment',
                      'om_account_cash_forecast.menu_cash_forecast_item',
                      'accounting_pdf_reports.menu_action_account_moves_ledger_general',
                      'accounting_pdf_reports.menu_account_report_bs',
                      'accounting_pdf_reports.menu_account_report'):
            self.assertIn(self.env.ref(xmlid).id, visible, xmlid)
        self.assertIn(self.env.ref('om_account_accountant.menu_review_journal_items').id, visible)
