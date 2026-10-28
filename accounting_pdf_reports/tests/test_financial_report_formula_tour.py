from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestFinancialReportFormulaTour(HttpCase):

    def test_balance_sheet_formula_details_are_visible(self):
        action = self.env.ref("accounting_pdf_reports.action_interactive_balance_sheet")
        self.start_tour(
            f"/odoo/action-{action.id}",
            "ff_balance_sheet_formula_info",
            login="admin",
        )
