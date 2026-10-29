from odoo.exceptions import AccessError, ValidationError
from odoo.tests import new_test_user, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged('post_install', '-at_install')
class TestInteractiveCustomerStatement(AccountTestInvoicingCommon):

    def test_period_partner_state_and_tag_filters(self):
        self.init_invoice('out_invoice', partner=self.partner_a, amounts=[100.0], taxes=[],
                          invoice_date='2025-02-10', post=True)
        self.init_invoice('out_invoice', partner=self.partner_b, amounts=[200.0], taxes=[],
                          invoice_date='2025-02-11', post=True)
        tag = self.env['res.partner.category'].create({'name': 'Statement Test'})
        self.partner_a.category_id = [(4, tag.id)]
        report = self.env['report.accounting_pdf_reports.customer_statement_data']

        result = report.get_interactive_data(
            period_type='custom', custom_date_from='2025-02-01', custom_date_to='2025-02-28',
            account_scopes=['receivable'], partner_ids=[self.partner_a.commercial_partner_id.id],
            partner_tag_ids=[tag.id], target_move='posted',
        )
        self.assertEqual(result['line_count'], 1)
        self.assertEqual(result['partners'][0]['id'], self.partner_a.commercial_partner_id.id)
        self.assertEqual(result['partners'][0]['lines'][0]['amount'], 100.0)
        self.assertEqual(result['date_from'], '2025-02-01')
        self.assertEqual(result['date_to'], '2025-02-28')

        without_tag_match = report.get_interactive_data(
            period_type='custom', custom_date_from='2025-02-01', custom_date_to='2025-02-28',
            account_scopes=['receivable'], partner_ids=[self.partner_b.commercial_partner_id.id],
            partner_tag_ids=[tag.id], target_move='posted',
        )
        self.assertEqual(without_tag_match['line_count'], 0)

    def test_access_and_filter_validation(self):
        report = self.env['report.accounting_pdf_reports.customer_statement_data']
        with self.assertRaises(ValidationError):
            report.get_interactive_data(account_scopes=['invalid'])
        user = new_test_user(
            self.env, login='statement_no_account', groups='base.group_user',
            company_id=self.env.company.id,
        )
        with self.assertRaises(AccessError):
            report.with_user(user).get_interactive_data()

    def test_vendor_statement_reports_payable_balance_as_positive(self):
        vendor = self.env['res.partner'].create({'name': 'Statement Vendor', 'supplier_rank': 1})
        self.init_invoice('in_invoice', partner=vendor, amounts=[125.0], taxes=[],
                          invoice_date='2025-02-12', post=True)
        result = self.env['report.accounting_pdf_reports.customer_statement_data'].get_interactive_data(
            period_type='custom', custom_date_from='2025-02-01', custom_date_to='2025-02-28',
            account_scopes=['payable'], partner_ids=[vendor.commercial_partner_id.id], target_move='posted',
        )
        self.assertEqual(result['line_count'], 1)
        self.assertEqual(result['partners'][0]['lines'][0]['amount'], 125.0)
        self.assertEqual(result['partners'][0]['lines'][0]['amount_currency'], 125.0)
        self.assertEqual(result['partners'][0]['amount'], 125.0)

    def test_print_and_send_preserve_report_filters(self):
        invoice = self.init_invoice('out_invoice', partner=self.partner_a, amounts=[80.0], taxes=[],
                                    invoice_date='2025-02-15', post=True)
        filters = {
            'period_type': 'custom',
            'custom_date_from': '2025-02-01',
            'custom_date_to': '2025-02-28',
            'account_scopes': ['receivable'],
            'partner_ids': [self.partner_a.commercial_partner_id.id],
            'partner_tag_ids': [],
            'target_move': 'posted',
            'scale': 'unit',
        }
        report = self.env['report.accounting_pdf_reports.customer_statement_data']

        print_action = report.get_print_action(filters)
        self.assertEqual(print_action['report_name'], 'accounting_pdf_reports.report_customer_statement')
        html, _report_type = self.env['ir.actions.report']._render_qweb_html(
            print_action['report_name'], print_action['context']['active_ids'],
        )
        self.assertIn(invoice.name.encode(), html)
        self.assertIn(b'80.00', html)

        send_action = report.get_send_action(filters)
        context = send_action['context']
        self.assertEqual(send_action['res_model'], 'mail.compose.message')
        recipients = self.env[context['default_model']].browse(context['default_res_ids'])
        self.assertEqual(recipients.mapped('customer_statement_partner_id'), self.partner_a.commercial_partner_id)
        self.assertEqual(context['default_composition_mode'], 'comment')
        self.assertIn(
            self.env.ref('accounting_pdf_reports.action_report_customer_statement'),
            self.env.ref('accounting_pdf_reports.email_template_customer_statement').report_template_ids,
        )
        composer = self.env['mail.compose.message'].with_context(context).create({})
        self.assertTrue(composer.attachment_ids)
        self.assertIn(invoice.name.encode(), bytes(composer.attachment_ids[0].raw))
