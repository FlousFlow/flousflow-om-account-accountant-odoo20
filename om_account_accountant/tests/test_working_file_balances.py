from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestWorkingFileBalances(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Account = cls.env["account.account"]
        cls.balance_sheet_account = Account.create({
            "code": "199801",
            "name": "Working File Balance Sheet Test",
            "account_type": "asset_current",
        })
        cls.income_account = Account.create({
            "code": "499801",
            "name": "Working File Income Statement Test",
            "account_type": "income",
        })

    def _post_balance_move(self, account, move_date, debit, credit):
        move = self.env["account.move"].create({
            "move_type": "entry",
            "date": move_date,
            "journal_id": self.company_data["default_journal_misc"].id,
            "line_ids": [
                (0, 0, {
                    "name": "Working file balance test",
                    "account_id": account.id,
                    "debit": debit,
                    "credit": credit,
                }),
                (0, 0, {
                    "name": "Working file balance test counterpart",
                    "account_id": self.company_data["default_account_expense"].id,
                    "debit": credit,
                    "credit": debit,
                }),
            ],
        })
        move.action_post()
        return move

    def test_balance_sheet_accounts_include_opening_balance_and_prior_year(self):
        self._post_balance_move(self.balance_sheet_account, "2024-06-01", 120, 0)
        self._post_balance_move(self.balance_sheet_account, "2025-02-01", 40, 0)
        self._post_balance_move(self.balance_sheet_account, "2026-03-01", 60, 0)
        self._post_balance_move(self.balance_sheet_account, "2026-07-01", 90, 0)
        self._post_balance_move(self.balance_sheet_account, "2026-04-01", 0, 10)
        self._post_balance_move(self.balance_sheet_account, "2026-05-01", 20, 0)

        working_file = self.env["account.working.file"].create({
            "name": "Working file balance sheet calculation",
            "date_from": "2026-01-01",
            "date_to": "2026-06-30",
        })
        line = working_file.balance_line_ids.filtered(
            lambda balance: balance.account_id == self.balance_sheet_account
        )

        self.assertEqual(len(line), 1)
        self.assertEqual(line.balance, 230)
        self.assertEqual(line.balance_previous, 160)
        self.assertEqual(line.variation, 70)
        self.assertEqual(line.variation_percent, 43.75)

    def test_income_statement_accounts_use_selected_period_only(self):
        self._post_balance_move(self.income_account, "2025-02-01", 0, 10)
        self._post_balance_move(self.income_account, "2025-07-01", 0, 70)
        self._post_balance_move(self.income_account, "2026-02-01", 0, 30)
        self._post_balance_move(self.income_account, "2026-07-01", 0, 50)

        working_file = self.env["account.working.file"].create({
            "name": "Working file income statement calculation",
            "date_from": "2026-01-01",
            "date_to": "2026-06-30",
        })
        line = working_file.balance_line_ids.filtered(
            lambda balance: balance.account_id == self.income_account
        )

        self.assertEqual(len(line), 1)
        self.assertEqual(line.balance, -30)
        self.assertEqual(line.balance_previous, -10)
        self.assertEqual(line.variation, -20)
        self.assertEqual(line.variation_percent, -200)

    def test_working_file_card_tracks_reviewed_balance_accounts(self):
        working_file = self.env["account.working.file"].create({
            "name": "Working file balance review progress",
            "date_from": "2026-01-01",
            "date_to": "2026-12-31",
        })
        line = working_file.balance_line_ids.filtered(
            lambda balance: balance.account_id == self.balance_sheet_account
        )

        self.assertEqual(working_file.balance_reviewed_count, 0)
        self.assertEqual(working_file.balance_line_count, len(working_file.balance_line_ids))
        self.assertEqual(working_file.balance_progress, 0)

        line.write({"state": "reviewed"})

        self.assertEqual(working_file.balance_reviewed_count, 1)
        self.assertAlmostEqual(
            working_file.balance_progress,
            100.0 / working_file.balance_line_count,
        )
