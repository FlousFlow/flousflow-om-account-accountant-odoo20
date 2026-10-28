from odoo import Command, fields
from odoo.tools.safe_eval import safe_eval
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestReviewAccrualCosts(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].with_company(cls.env.company).create({
            "name": "Review accrual cost test product",
            "type": "service",
            "invoice_policy": "delivery",
            "uom_id": cls.uom.id,
            "standard_price": 125.0,
            "list_price": 400.0,
            "taxes_id": [Command.clear()],
        })

    def _create_order_line(self, invoice_policy="delivery", quantity=5.0):
        self.product.invoice_policy = invoice_policy
        order = self.env["sale.order"].sudo().create({
            "partner_id": self.partner_a.id,
            "order_line": [Command.create({
                "product_id": self.product.id,
                "product_uom_qty": quantity,
                "price_unit": 400.0,
                "tax_ids": [Command.clear()],
            })],
        })
        order.action_confirm()
        return order, order.order_line

    def test_invoice_to_be_issued_cost_uses_delivered_quantity(self):
        _order, line = self._create_order_line()
        line.qty_delivered = 3.0

        report_line = line.with_context(
            accrual_entry_date=fields.Date.to_string(fields.Date.today()),
        )

        self.assertEqual(report_line.qty_delivered_at_date, 3.0)
        self.assertAlmostEqual(report_line.review_accrual_unit_cost, 125.0)
        self.assertAlmostEqual(report_line.review_accrual_delivered_total_cost, 375.0)

        grouped_rows = self.env["sale.order.line"].sudo().with_context(
            accrual_entry_date=fields.Date.to_string(fields.Date.today()),
        )._read_group(
            [("id", "=", line.id)],
            ["order_partner_id"],
            ["review_accrual_delivered_total_cost:sum"],
        )
        self.assertEqual(grouped_rows[0][1], 375.0)

    def test_invoiced_not_delivered_cost_uses_invoiced_quantity(self):
        _order, line = self._create_order_line(invoice_policy="order", quantity=2.0)
        invoice = line.order_id._create_invoices()
        invoice.action_post()

        report_line = line.with_context(
            accrual_entry_date=fields.Date.to_string(fields.Date.today()),
        )

        self.assertEqual(report_line.qty_invoiced_at_date, 2.0)
        self.assertAlmostEqual(report_line.review_accrual_unit_cost, 125.0)
        self.assertAlmostEqual(report_line.review_accrual_invoiced_total_cost, 250.0)

    def test_review_accrual_actions_default_to_enterprise_grouping_and_period(self):
        purchase_action = self.env.ref(
            "om_account_accountant.action_purchase_bill_to_receive"
        )
        purchase_context = safe_eval(purchase_action.context)
        self.assertEqual(purchase_context["search_default_order_date_last_year"], 1)
        self.assertEqual(purchase_context["search_default_groupby_supplier"], 1)

        sale_action = self.env.ref("om_account_accountant.action_sale_invoice_to_be_issued")
        sale_context = safe_eval(sale_action.context)
        self.assertEqual(sale_context["search_default_review_order_date_last_year"], 1)
        self.assertEqual(sale_context["search_default_review_groupby_customer"], 1)
