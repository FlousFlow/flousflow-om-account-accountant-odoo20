from odoo.exceptions import ValidationError
from odoo.tests import HttpCase, TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestDeferredSchedulePeriods(TransactionCase):

    def setUp(self):
        super().setUp()
        self.report = self.env["account.deferred.schedule.report"]

    def test_month_and_quarter_ranges_and_previous_periods(self):
        month_ranges = self.report._get_period_ranges(
            "month", period_anchor="2026-10-28", comparison_periods=1
        )
        self.assertEqual(
            [(item["date_from"], item["date_to"]) for item in month_ranges],
            [("2026-10-01", "2026-10-31"), ("2026-09-01", "2026-09-30")],
        )

        quarter_ranges = self.report._get_period_ranges(
            "quarter", period_anchor="2026-10-28", comparison_periods=1
        )
        self.assertEqual(
            [(item["label"], item["date_from"], item["date_to"]) for item in quarter_ranges],
            [("Q4 2026", "2026-10-01", "2026-12-31"), ("Q3 2026", "2026-07-01", "2026-09-30")],
        )

    def test_fiscal_year_ranges_use_company_settings(self):
        self.env.company.write({"fiscalyear_last_day": 30, "fiscalyear_last_month": "6"})

        ranges = self.report._get_period_ranges(
            "fiscal_year", period_anchor="2026-10-28", comparison_periods=1
        )

        self.assertEqual(
            [(item["date_from"], item["date_to"]) for item in ranges],
            [("2026-07-01", "2027-06-30"), ("2025-07-01", "2026-06-30")],
        )

    def test_custom_range_compares_with_an_equal_length_prior_range(self):
        ranges = self.report._get_period_ranges(
            "custom", date_from="2026-09-10", date_to="2026-09-19", comparison_periods=2
        )

        self.assertEqual(
            [(item["date_from"], item["date_to"]) for item in ranges],
            [
                ("2026-09-10", "2026-09-19"),
                ("2026-08-31", "2026-09-09"),
                ("2026-08-21", "2026-08-30"),
            ],
        )

    def test_invalid_custom_range_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.report._get_period_ranges(
                "custom", date_from="2026-09-20", date_to="2026-09-10"
            )


@tagged("post_install", "-at_install")
class TestDeferredSchedulePeriodsTour(HttpCase):

    def test_deferred_schedule_period_picker(self):
        action = self.env.ref("om_account_accountant.action_deferred_expense_report")
        self.start_tour(
            f"/odoo/action-{action.id}",
            "ff_deferred_schedule_periods",
            login="admin",
        )
