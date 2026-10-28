from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestJournalAuditPeriodFilterTour(HttpCase):

    def test_journal_audit_period_filter(self):
        action = self.env.ref("om_account_accountant.action_journal_audit")
        self.start_tour(
            f"/odoo/action-{action.id}",
            "ff_journal_audit_period_filter",
            login="admin",
        )
