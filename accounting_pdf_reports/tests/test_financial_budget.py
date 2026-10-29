from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged('post_install', '-at_install')
class TestInteractiveFinancialBudget(AccountTestInvoicingCommon):

    def test_profit_and_loss_displays_account_budget_amounts(self):
        invoice = self.init_invoice(
            'out_invoice', amounts=[1000.0], invoice_date='2026-03-15', taxes=[], post=True,
        )
        account = invoice.invoice_line_ids.account_id
        budget = self.env['account.financial.budget'].create({
            'name': 'FY 2026 test budget',
            'date_from': '2026-01-01',
            'date_to': '2026-12-31',
            'company_id': self.env.company.id,
            'line_ids': [(0, 0, {'account_id': account.id, 'planned_amount': 12000.0})],
        })
        report = self.env.ref('accounting_pdf_reports.account_financial_report_profitandloss0')

        data = self.env['report.accounting_pdf_reports.report_financial'].get_interactive_data(
            report.id, '2026-01-01', '2026-12-31', financial_budget_id=budget.id,
        )

        account_line = next(line for line in data['lines'] if line.get('account_id') == account.id)
        self.assertEqual(account_line['budget_amount'], 12000.0)
        self.assertTrue(account_line['budget_line_id'])
        self.assertEqual(data['financial_budget']['id'], budget.id)

    def test_profit_and_loss_prorates_budget_for_selected_date_range(self):
        invoice = self.init_invoice(
            'out_invoice', amounts=[1000.0], invoice_date='2026-03-15', taxes=[], post=True,
        )
        account = invoice.invoice_line_ids.account_id
        budget = self.env['account.financial.budget'].create({
            'name': 'FY 2026 prorated budget',
            'date_from': '2026-01-01',
            'date_to': '2026-12-31',
            'company_id': self.env.company.id,
            'line_ids': [(0, 0, {'account_id': account.id, 'planned_amount': 12000.0})],
        })
        report = self.env.ref('accounting_pdf_reports.account_financial_report_profitandloss0')

        data = self.env['report.accounting_pdf_reports.report_financial'].get_interactive_data(
            report.id, '2026-01-01', '2026-03-31', financial_budget_id=budget.id,
        )

        account_line = next(line for line in data['lines'] if line.get('account_id') == account.id)
        self.assertAlmostEqual(account_line['budget_amount'], 12000.0 * 90 / 365)
