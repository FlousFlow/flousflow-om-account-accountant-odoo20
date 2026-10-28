from odoo import api, fields, models, _
from odoo.exceptions import AccessError, ValidationError


class AccountJournalAuditReport(models.AbstractModel):
    _name = "account.journal.audit.report"
    _description = "Interactive Journal Audit Report"

    _REVIEW_LABELS = {
        "no_review": "No Review",
        "todo": "To Review",
        "anomaly": "Anomaly",
        "reviewed": "Reviewed",
        "supervised": "Supervised",
    }

    @api.model
    def _get_report_filters(self, date_from, date_to, target_move, include_payments=False):
        date_from = fields.Date.to_date(date_from)
        date_to = fields.Date.to_date(date_to)
        if not date_from or not date_to or date_from > date_to:
            raise ValidationError(_("Choose a valid date range."))
        if target_move not in ("posted", "draft", "all"):
            raise ValidationError(_("Unsupported journal entry filter."))

        move_domain = [
            ("company_id", "=", self.env.company.id),
            ("date", ">=", date_from),
            ("date", "<=", date_to),
            ("state", "!=", "cancel"),
        ]
        line_domain = [
            ("company_id", "=", self.env.company.id),
            ("date", ">=", date_from),
            ("date", "<=", date_to),
            ("parent_state", "!=", "cancel"),
        ]
        if target_move == "posted":
            move_domain.append(("state", "=", "posted"))
            line_domain.append(("parent_state", "=", "posted"))
        elif target_move == "draft":
            move_domain.append(("state", "=", "draft"))
            line_domain.append(("parent_state", "=", "draft"))
        if not include_payments:
            move_domain.append(("origin_payment_id", "=", False))
            line_domain.append(("move_id.origin_payment_id", "=", False))
        return date_from, date_to, move_domain, line_domain

    @api.model
    def get_report_data(self, date_from, date_to, target_move="posted", include_payments=False):
        """Return a company-scoped journal and tax summary using the current user's rights."""
        date_from, date_to, move_domain, line_domain = self._get_report_filters(
            date_from, date_to, target_move, include_payments
        )
        move_groups = self.env["account.move"]._read_group(
            move_domain, ["journal_id", "review_state"], ["__count"]
        )
        line_groups = self.env["account.move.line"]._read_group(
            line_domain,
            ["journal_id"],
            ["debit:sum", "credit:sum", "balance:sum"],
        )

        journals = {}
        for journal, review_state, count in move_groups:
            if not journal:
                continue
            row = journals.setdefault(journal.id, {
                "id": journal.id,
                "name": journal.display_name,
                "documents": 0,
                "to_review": 0,
                "debit": 0.0,
                "credit": 0.0,
                "balance": 0.0,
            })
            row["documents"] += count
            if review_state in ("todo", "anomaly"):
                row["to_review"] += count

        for journal, debit, credit, balance in line_groups:
            if journal and journal.id in journals:
                journals[journal.id].update({
                    "debit": debit or 0.0,
                    "credit": credit or 0.0,
                    "balance": balance or 0.0,
                })

        tax_groups = self.env["account.move.line"]._read_group(
            line_domain + [("tax_line_id", "!=", False)],
            ["tax_line_id"],
            ["tax_base_amount:sum", "debit:sum", "credit:sum", "balance:sum"],
        )
        taxes = [
            {
                "id": tax.id,
                "name": tax.display_name,
                "base": base or 0.0,
                "debit": debit or 0.0,
                "credit": credit or 0.0,
                "balance": balance or 0.0,
            }
            for tax, base, debit, credit, balance in tax_groups
            if tax
        ]

        currency = self.env.company.currency_id
        return {
            "journals": sorted(journals.values(), key=lambda row: row["name"].casefold()),
            "taxes": taxes,
            "currency_id": currency.id,
            "company_id": self.env.company.id,
            "company_name": self.env.company.display_name,
            "can_audit": self.env.user.has_group("account.group_account_user")
            or self.env.user.has_group("account.group_account_manager"),
        }

    @api.model
    def get_journal_moves(self, journal_id, date_from, date_to, target_move="posted", include_payments=False, offset=0, limit=100):
        """Load one page of journal documents for an expanded report row."""
        date_from, date_to, move_domain, _line_domain = self._get_report_filters(
            date_from, date_to, target_move, include_payments
        )
        journal = self.env["account.journal"].browse(int(journal_id)).exists()
        if not journal or journal.company_id != self.env.company:
            raise AccessError(_("The selected journal is outside the active company."))
        move_domain.append(("journal_id", "=", journal.id))
        offset = max(0, int(offset))
        limit = min(max(1, int(limit)), 200)
        moves = self.env["account.move"].search(
            move_domain, order="date, name, id", offset=offset, limit=limit + 1
        )
        has_more = len(moves) > limit
        moves = moves[:limit]
        line_totals = {}
        if moves:
            for move, debit, credit, balance in self.env["account.move.line"]._read_group(
                [("move_id", "in", moves.ids)],
                ["move_id"],
                ["debit:sum", "credit:sum", "balance:sum"],
            ):
                if move:
                    line_totals[move.id] = (debit or 0.0, credit or 0.0, balance or 0.0)

        move_type_labels = dict(
            self.env["account.move"]._fields["move_type"]._description_selection(self.env)
        )
        return {
            "rows": [
                {
                    "id": move.id,
                    "date": fields.Date.to_string(move.date),
                    "name": move.name,
                    "ref": move.ref or "",
                    "document_type": move_type_labels.get(move.move_type, move.move_type),
                    "state": move.state,
                    "review_state": self._REVIEW_LABELS.get(move.review_state, move.review_state),
                    "debit": line_totals.get(move.id, (0.0, 0.0, 0.0))[0],
                    "credit": line_totals.get(move.id, (0.0, 0.0, 0.0))[1],
                    "balance": line_totals.get(move.id, (0.0, 0.0, 0.0))[2],
                }
                for move in moves
            ],
            "offset": offset + len(moves),
            "has_more": has_more,
        }

    @api.model
    def mark_journal_reviewed(self, journal_id, date_from, date_to, include_payments=False):
        """Mark only posted entries still awaiting review in this journal and period."""
        if not (
            self.env.user.has_group("account.group_account_user")
            or self.env.user.has_group("account.group_account_manager")
        ):
            raise AccessError(_("Only accounting users can mark journal entries as reviewed."))
        _date_from, _date_to, move_domain, _line_domain = self._get_report_filters(
            date_from, date_to, "posted", include_payments
        )
        journal = self.env["account.journal"].browse(int(journal_id)).exists()
        if not journal or journal.company_id != self.env.company:
            raise AccessError(_("The selected journal is outside the active company."))
        move_domain += [
            ("journal_id", "=", journal.id),
            ("review_state", "in", ["todo", "anomaly"]),
        ]
        moves = self.env["account.move"].search(move_domain)
        count = len(moves)
        moves.set_moves_checked()
        return count
