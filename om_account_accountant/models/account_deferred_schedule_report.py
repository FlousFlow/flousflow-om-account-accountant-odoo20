from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, ValidationError


class AccountDeferredScheduleReport(models.AbstractModel):
    _name = "account.deferred.schedule.report"
    _description = "Deferred Expense and Revenue Report"

    @api.model
    def _check_report_access(self):
        if not any(self.env.user.has_group(group) for group in (
            "account.group_account_readonly",
            "account.group_account_invoice",
            "account.group_account_user",
            "account.group_account_manager",
        )):
            raise AccessError(_("You are not allowed to read deferred schedule reports."))

    @api.model
    def _get_period_dates(self, period):
        try:
            start = fields.Date.to_date(f"{period}-01")
        except (TypeError, ValueError):
            start = False
        if not start or fields.Date.to_string(start)[:7] != period:
            raise ValidationError(_("Choose a valid reporting month."))
        return start, start + relativedelta(months=1, days=-1)

    @api.model
    def _validate_filters(self, report_type, group_by, target_move):
        if report_type not in ("expense", "revenue"):
            raise ValidationError(_("Unsupported deferred report."))
        if group_by not in ("account", "category", "product"):
            raise ValidationError(_("Unsupported grouping."))
        if target_move not in ("posted", "all"):
            raise ValidationError(_("Unsupported journal entry filter."))

    @api.model
    def _get_move_domain(self, report_type, date_from, date_to, target_move):
        asset_type = "purchase" if report_type == "expense" else "sale"
        domain = [
            ("company_id", "=", self.env.company.id),
            ("date", ">=", date_from),
            ("date", "<=", date_to),
            ("depreciation_asset_id", "!=", False),
            ("depreciation_asset_id.category_id.type", "=", asset_type),
            ("asset_entry_type", "=", "depreciation"),
            ("state", "!=", "cancel"),
        ]
        if target_move == "posted":
            domain.append(("state", "=", "posted"))
        return domain

    @api.model
    def _get_group(self, report_type, group_by, asset, account):
        if group_by == "account":
            group = account
        elif group_by == "category":
            group = asset.category_id
        else:
            group = asset.invoice_line_id.product_id or asset
        if not group:
            return False, False, False, False
        group_model = group._name
        return f"{group_by}:{group_model}:{group.id}", group.id, group.display_name, group_model

    @api.model
    def _collect_period(self, report_type, period, group_by, target_move, journal_ids):
        date_from, date_to = self._get_period_dates(period)
        domain = self._get_move_domain(report_type, date_from, date_to, target_move)
        if journal_ids:
            domain.append(("journal_id", "in", journal_ids))
        moves = self.env["account.move"].search(domain, order="date, name, id")
        rows = {}
        if not moves:
            return rows

        asset_by_id = {asset.id: asset for asset in moves.depreciation_asset_id}
        if report_type == "expense":
            account_by_asset = {
                asset_id: asset.category_id.account_depreciation_expense_id.id
                for asset_id, asset in asset_by_id.items()
            }
            sign = 1
        else:
            account_by_asset = {
                asset_id: asset.category_id.account_depreciation_id.id
                for asset_id, asset in asset_by_id.items()
            }
            sign = -1
        account_ids = list({account_id for account_id in account_by_asset.values() if account_id})
        lines = self.env["account.move.line"].search([
            ("move_id", "in", moves.ids),
            ("account_id", "in", account_ids),
            ("company_id", "=", self.env.company.id),
        ]) if account_ids else self.env["account.move.line"]

        recognized_by_move = {}
        account_by_move = {}
        for line in lines:
            asset_id = line.move_id.depreciation_asset_id.id
            if line.account_id.id != account_by_asset.get(asset_id):
                continue
            recognized_by_move[line.move_id.id] = recognized_by_move.get(line.move_id.id, 0.0) + sign * line.balance
            account_by_move[line.move_id.id] = line.account_id

        for move in moves:
            asset = asset_by_id.get(move.depreciation_asset_id.id)
            account = account_by_move.get(move.id)
            key, group_id, name, group_model = self._get_group(report_type, group_by, asset, account)
            if not key:
                continue
            row = rows.setdefault(key, {
                "key": key,
                "group_id": group_id,
                "group_model": group_model,
                "name": name,
                "amount": 0.0,
                "entries": 0,
                "move_ids": [],
            })
            row["amount"] += recognized_by_move.get(move.id, 0.0)
            row["entries"] += 1
            row["move_ids"].append(move.id)
        return rows

    @api.model
    def get_report_data(
        self, report_type, period, group_by="account", target_move="posted",
        compare_previous=False, hide_zero=False, journal_ids=None,
    ):
        """Aggregate the local asset/revenue-recognition board using posted journal amounts."""
        self._check_report_access()
        self._validate_filters(report_type, group_by, target_move)
        journal_ids = self._validate_journals(journal_ids)
        date_from, _date_to = self._get_period_dates(period)
        current = self._collect_period(report_type, period, group_by, target_move, journal_ids)
        previous_period = fields.Date.to_string(date_from - relativedelta(months=1))[:7]
        previous = (
            self._collect_period(report_type, previous_period, group_by, target_move, journal_ids)
            if compare_previous else {}
        )
        currency = self.env.company.currency_id
        rows = []
        for key in current.keys() | previous.keys():
            now = current.get(key, {})
            before = previous.get(key, {})
            amount = now.get("amount", 0.0)
            previous_amount = before.get("amount", 0.0)
            if hide_zero and currency.is_zero(amount) and currency.is_zero(previous_amount):
                continue
            base = now or before
            rows.append({
                "key": key,
                "group_id": base["group_id"],
                "group_model": base["group_model"],
                "name": base["name"],
                "entries": now.get("entries", 0),
                "amount": amount,
                "previous_amount": previous_amount,
                "move_ids": now.get("move_ids", []),
            })
        rows.sort(key=lambda row: row["name"].casefold())
        return {
            "report_type": report_type,
            "period": period,
            "previous_period": previous_period,
            "group_by": group_by,
            "rows": rows,
            "currency_id": currency.id,
            "company_name": self.env.company.display_name,
            "journals": [
                {"id": journal.id, "name": journal.display_name}
                for journal in self.env["account.journal"].search([
                    ("company_id", "=", self.env.company.id),
                    ("type", "in", ("general", "purchase", "sale", "bank", "cash")),
                ], order="sequence, name, id")
            ],
        }

    @api.model
    def _validate_journals(self, journal_ids):
        try:
            ids = sorted({int(journal_id) for journal_id in (journal_ids or [])})
        except (TypeError, ValueError):
            raise ValidationError(_("Choose valid journals."))
        journals = self.env["account.journal"].search([
            ("id", "in", ids),
            ("company_id", "=", self.env.company.id),
        ]) if ids else self.env["account.journal"]
        if ids and set(ids) != set(journals.ids):
            raise AccessError(_("One or more selected journals are outside the active company."))
        return ids

    @api.model
    def get_group_move_domain(
        self, report_type, period, group_by, group_id, target_move="posted",
        group_model=None, journal_ids=None,
    ):
        self._check_report_access()
        self._validate_filters(report_type, group_by, target_move)
        journal_ids = self._validate_journals(journal_ids)
        date_from, date_to = self._get_period_dates(period)
        domain = self._get_move_domain(report_type, date_from, date_to, target_move)
        if journal_ids:
            domain.append(("journal_id", "in", journal_ids))
        group_id = int(group_id)
        if group_by == "category":
            domain.append(("depreciation_asset_id.category_id", "=", group_id))
        elif group_by == "product":
            if group_model == "product.product":
                domain.append(("depreciation_asset_id.invoice_line_id.product_id", "=", group_id))
            else:
                domain.append(("depreciation_asset_id", "=", group_id))
        else:
            account_field = "account_depreciation_expense_id" if report_type == "expense" else "account_depreciation_id"
            domain.append((f"depreciation_asset_id.category_id.{account_field}", "=", group_id))
        return domain
