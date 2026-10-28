from datetime import date

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestJournalAuditPeriods(TransactionCase):

    def test_fiscal_year_range_uses_active_company_settings(self):
        company = self.env.company
        company.write({
            "fiscalyear_last_day": 30,
            "fiscalyear_last_month": "6",
        })
        anchor = date(2026, 10, 28)

        result = self.env["account.journal.audit.report"].get_fiscal_year_range(anchor)

        self.assertEqual(result, {
            "date_from": "2026-07-01",
            "date_to": "2027-06-30",
        })

    def test_fiscal_year_range_defaults_to_today(self):
        today = fields.Date.context_today(self.env.company)
        expected = self.env.company.compute_fiscalyear_dates(today)

        result = self.env["account.journal.audit.report"].get_fiscal_year_range()

        self.assertEqual(result["date_from"], fields.Date.to_string(expected["date_from"]))
        self.assertEqual(result["date_to"], fields.Date.to_string(expected["date_to"]))
