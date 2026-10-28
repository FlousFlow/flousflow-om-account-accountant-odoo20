from datetime import timedelta

from odoo import Command, fields
from odoo.tools.safe_eval import safe_eval
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import HttpCase, tagged


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
        ).formatted_read_group(
            [("id", "=", line.id)],
            ["order_partner_id"],
            ["review_accrual_delivered_total_cost:sum"],
        )
        self.assertEqual(grouped_rows[0]["review_accrual_delivered_total_cost:sum"], 375.0)

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

        yesterday = fields.Date.to_string(fields.Date.today() - timedelta(days=1))
        historical_line = line.with_context(accrual_entry_date=yesterday)
        self.assertEqual(historical_line.qty_invoiced_at_date, 0.0)
        self.assertAlmostEqual(historical_line.review_accrual_invoiced_total_cost, 0.0)
        self.assertFalse(
            self.env["sale.order.line"].with_context(accrual_entry_date=yesterday).search(
                [("id", "=", line.id), ("deferred_revenue", "in", [True])]
            )
        )

    def test_purchase_review_search_and_group_sums_use_as_of_context(self):
        product = self.env["product.product"].sudo().with_company(self.env.company).create({
            "name": "Purchase review accrual test product",
            "type": "service",
            "uom_id": self.uom.id,
            "standard_price": 100.0,
            "list_price": 150.0,
            "taxes_id": [Command.clear()],
            "supplier_taxes_id": [Command.clear()],
        })
        order = self.env["purchase.order"].sudo().create({
            "partner_id": self.partner_a.id,
            "order_line": [Command.create({
                "product_id": product.id,
                "product_qty": 5.0,
                "price_unit": 100.0,
                "tax_ids": [Command.clear()],
            })],
        })
        order.button_confirm()
        line = order.order_line
        line.qty_received_manual = 5.0
        order.action_create_invoice()
        invoice = order.invoice_ids
        invoice.invoice_date = fields.Date.today()
        invoice.action_post()
        self.assertEqual(line.qty_invoiced, 5.0, invoice.invoice_line_ids.mapped("quantity"))

        today = fields.Date.to_string(fields.Date.today())
        yesterday = fields.Date.to_string(fields.Date.today() - timedelta(days=1))
        purchase_lines = self.env["purchase.order.line"]
        self.assertIn(
            line,
            purchase_lines.with_context(accrual_entry_date=yesterday)._get_accrual_line_ids(
                "bill_to_receive"
            ),
        )
        self.assertNotIn(
            line,
            purchase_lines.with_context(accrual_entry_date=today)._get_accrual_line_ids(
                "bill_to_receive"
            ),
        )

        historical_line = line.with_context(accrual_entry_date=yesterday)
        self.assertEqual(historical_line.qty_received_at_date, 5.0)
        self.assertEqual(historical_line.qty_invoiced_at_date, 0.0)
        grouped_rows = purchase_lines.with_context(
            accrual_entry_date=yesterday,
        ).formatted_read_group(
            [("id", "=", line.id)],
            ["partner_id"],
            ["qty_received_at_date:sum", "qty_invoiced_at_date:sum"],
        )
        self.assertEqual(grouped_rows[0]["qty_received_at_date:sum"], 5.0)
        self.assertEqual(grouped_rows[0]["qty_invoiced_at_date:sum"], 0.0)

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

    def test_review_accrual_reports_use_their_own_list_views(self):
        report_mappings = (
            (
                "action_purchase_bill_to_receive_list",
                "action_purchase_bill_to_receive",
                "view_purchase_bill_to_receive_list",
            ),
            (
                "action_purchase_billed_not_received_list",
                "action_purchase_billed_not_received",
                "view_purchase_billed_not_received_list",
            ),
            (
                "action_sale_invoice_to_be_issued_list",
                "action_sale_invoice_to_be_issued",
                "view_sale_invoice_to_be_issued_list",
            ),
            (
                "action_sale_invoiced_not_delivered_list",
                "action_sale_invoiced_not_delivered",
                "view_sale_invoiced_not_delivered_list",
            ),
        )
        for mapping_xmlid, action_xmlid, view_xmlid in report_mappings:
            with self.subTest(mapping=mapping_xmlid):
                mapping = self.env.ref(f"om_account_accountant.{mapping_xmlid}")
                self.assertEqual(
                    mapping.act_window_id,
                    self.env.ref(f"om_account_accountant.{action_xmlid}"),
                )
                self.assertEqual(
                    mapping.view_id,
                    self.env.ref(f"om_account_accountant.{view_xmlid}"),
                )


@tagged("post_install", "-at_install")
class TestReviewAccrualDatePicker(HttpCase):

    def test_review_accrual_date_picker(self):
        action = self.env.ref("om_account_accountant.action_purchase_bill_to_receive")
        self.start_tour(
            f"/odoo/action-{action.id}",
            "ff_review_accrual_date_picker",
            login="admin",
        )
