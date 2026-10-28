/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { formatMonetary } from "@web/views/fields/formatters";
import { standardActionServiceProps } from "@web/webclient/actions/action_plugin";
import { Component, onWillStart, proxy, useProps } from "@odoo/owl";

const { DateTime } = luxon;
const PAGE_SIZE = 100;

export class JournalAudit extends Component {
    static template = "om_account_accountant.JournalAudit";
    props = useProps(standardActionServiceProps);

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.state = proxy({
            periodType: "fiscal_year",
            periodAnchor: DateTime.now().toISODate(),
            periodFilterOpen: false,
            dateFrom: "",
            dateTo: "",
            customDateFrom: "",
            customDateTo: "",
            customDateError: "",
            targetMove: "posted",
            includePayments: false,
            displayScale: 1,
            loading: true,
            journals: [],
            taxes: [],
            currencyId: false,
            companyId: false,
            companyName: "",
            canAudit: false,
            expanded: [],
            movePages: {},
            auditingJournalId: false,
            settingsOpen: false,
        });
        onWillStart(async () => {
            await this.setPeriod("fiscal_year", this.state.periodAnchor, false, false);
            await this.loadReport();
        });
    }

    get dateFrom() {
        return this.state.dateFrom;
    }

    get dateTo() {
        return this.state.dateTo;
    }

    get periodLabel() {
        if (this.state.periodType === "month") {
            return DateTime.fromISO(this.state.periodAnchor).toFormat("LLLL yyyy");
        }
        if (this.state.periodType === "quarter") {
            const anchor = DateTime.fromISO(this.state.periodAnchor);
            return `Q${anchor.quarter} ${anchor.year}`;
        }
        if (this.state.periodType === "custom") {
            const from = DateTime.fromISO(this.state.dateFrom).toLocaleString(DateTime.DATE_SHORT);
            const to = DateTime.fromISO(this.state.dateTo).toLocaleString(DateTime.DATE_SHORT);
            return `${from} – ${to}`;
        }
        const fromYear = DateTime.fromISO(this.state.dateFrom).year;
        const toYear = DateTime.fromISO(this.state.dateTo).year;
        return fromYear === toYear ? String(fromYear) : `${fromYear}–${toYear}`;
    }

    getPeriodOptionLabel(periodType) {
        const anchor = DateTime.fromISO(this.state.periodAnchor);
        if (periodType === "month") {
            return anchor.toFormat("LLLL yyyy");
        }
        if (periodType === "quarter") {
            return `Q${anchor.quarter} ${anchor.year}`;
        }
        return String(anchor.year);
    }

    togglePeriodFilter() {
        this.state.periodFilterOpen = !this.state.periodFilterOpen;
    }

    async setPeriod(periodType, anchorDate = this.state.periodAnchor, keepMenuOpen = false, reload = true) {
        const anchor = DateTime.fromISO(anchorDate);
        if (!anchor.isValid || !["month", "quarter", "fiscal_year"].includes(periodType)) {
            return;
        }
        this.state.periodType = periodType;
        this.state.periodAnchor = anchor.toISODate();
        this.state.periodFilterOpen = keepMenuOpen;

        let dateFrom;
        let dateTo;
        if (periodType === "fiscal_year") {
            const range = await this.orm.call(
                "account.journal.audit.report",
                "get_fiscal_year_range",
                [this.state.periodAnchor]
            );
            dateFrom = range.date_from;
            dateTo = range.date_to;
        } else {
            const range = periodType === "month" ? "month" : "quarter";
            dateFrom = anchor.startOf(range).toISODate();
            dateTo = anchor.endOf(range).toISODate();
        }
        this.state.dateFrom = dateFrom;
        this.state.dateTo = dateTo;
        if (periodType !== "custom") {
            this.state.customDateFrom = dateFrom;
            this.state.customDateTo = dateTo;
        }
        if (reload) {
            await this.loadReport();
        }
    }

    async navigatePeriod(periodType, offset) {
        const units = { month: "months", quarter: "quarters", fiscal_year: "years" };
        const anchor = DateTime.fromISO(this.state.periodAnchor).plus({ [units[periodType]]: offset });
        await this.setPeriod(periodType, anchor.toISODate(), true);
    }

    async onCustomDateFromChange(ev) {
        this.state.customDateFrom = ev.target.value;
        await this.applyCustomDateRange();
    }

    async onCustomDateToChange(ev) {
        this.state.customDateTo = ev.target.value;
        await this.applyCustomDateRange();
    }

    async applyCustomDateRange() {
        const from = DateTime.fromISO(this.state.customDateFrom);
        const to = DateTime.fromISO(this.state.customDateTo);
        if (!from.isValid || !to.isValid) {
            this.state.customDateError = this.state.customDateFrom && this.state.customDateTo
                ? _t("Enter valid start and end dates.")
                : "";
            return;
        }
        if (from > to) {
            this.state.customDateError = _t("The start date must be on or before the end date.");
            return;
        }
        this.state.customDateError = "";
        this.state.periodType = "custom";
        this.state.periodAnchor = from.toISODate();
        this.state.dateFrom = from.toISODate();
        this.state.dateTo = to.toISODate();
        await this.loadReport();
    }

    get totals() {
        return this.state.journals.reduce((total, row) => ({
            documents: total.documents + row.documents,
            toReview: total.toReview + row.to_review,
            debit: total.debit + row.debit,
            credit: total.credit + row.credit,
            balance: total.balance + row.balance,
        }), { documents: 0, toReview: 0, debit: 0, credit: 0, balance: 0 });
    }

    async loadReport() {
        this.state.loading = true;
        try {
            const data = await this.orm.call(
                "account.journal.audit.report",
                "get_report_data",
                [this.dateFrom, this.dateTo, this.state.targetMove, this.state.includePayments]
            );
            this.state.journals = data.journals;
            this.state.taxes = data.taxes;
            this.state.currencyId = data.currency_id;
            this.state.companyId = data.company_id;
            this.state.companyName = data.company_name;
            this.state.canAudit = data.can_audit;
            this.state.expanded = [];
            this.state.movePages = {};
        } catch (error) {
            this.notification.add(error.message || _t("The Journal Audit report could not be loaded."), {
                type: "danger",
                sticky: true,
            });
        } finally {
            this.state.loading = false;
        }
    }

    async onTargetMoveChange(ev) {
        this.state.targetMove = ev.target.value;
        await this.loadReport();
    }

    async onPaymentsChange(ev) {
        this.state.includePayments = ev.target.checked;
        await this.loadReport();
    }

    onDisplayScaleChange(ev) {
        this.state.displayScale = Number(ev.target.value) || 1;
    }

    toggleSettings() {
        this.state.settingsOpen = !this.state.settingsOpen;
    }

    exportXlsx() {
        this.state.settingsOpen = false;
        const params = new URLSearchParams({
            date_from: this.dateFrom,
            date_to: this.dateTo,
            target_move: this.state.targetMove,
            include_payments: this.state.includePayments ? "1" : "0",
            scale: String(this.state.displayScale),
        });
        return this.action.doAction({
            type: "ir.actions.act_url",
            url: `/om_account_accountant/journal_audit/xlsx?${params.toString()}`,
            target: "download",
        });
    }

    formatAmount(value) {
        return formatMonetary((value || 0) / this.state.displayScale, { currencyId: this.state.currencyId });
    }

    async toggleJournal(journal) {
        const key = journal.id;
        if (this.state.expanded.includes(key)) {
            this.state.expanded = this.state.expanded.filter((id) => id !== key);
            return;
        }
        this.state.expanded = [...this.state.expanded, key];
        if (!this.state.movePages[key]) {
            this.state.movePages[key] = { rows: [], offset: 0, hasMore: false, loading: true };
            await this.loadJournalMoves(journal.id, 0);
        }
    }

    async loadJournalMoves(journalId, offset) {
        const key = journalId;
        const current = this.state.movePages[key] || { rows: [], offset: 0, hasMore: false };
        this.state.movePages[key] = { ...current, loading: true };
        try {
            const result = await this.orm.call(
                "account.journal.audit.report",
                "get_journal_moves",
                [journalId, this.dateFrom, this.dateTo, this.state.targetMove, this.state.includePayments, offset, PAGE_SIZE]
            );
            this.state.movePages[key] = {
                rows: [...current.rows, ...result.rows],
                offset: result.offset,
                hasMore: result.has_more,
                loading: false,
            };
        } catch (error) {
            this.state.movePages[key] = { ...current, loading: false };
            this.notification.add(error.message || _t("Journal entries could not be loaded."), {
                type: "danger",
            });
        }
    }

    async auditJournal(journal) {
        if (!this.state.canAudit || !journal.to_review || this.state.auditingJournalId) {
            return;
        }
        this.state.auditingJournalId = journal.id;
        try {
            const count = await this.orm.call(
                "account.journal.audit.report",
                "mark_journal_reviewed",
                [journal.id, this.dateFrom, this.dateTo, this.state.includePayments]
            );
            this.notification.add(_t("%s entries marked as reviewed.", count), {
                type: "success",
            });
            await this.loadReport();
        } catch (error) {
            this.notification.add(error.message || _t("The journal could not be marked as reviewed."), {
                type: "danger",
                sticky: true,
            });
        } finally {
            this.state.auditingJournalId = false;
        }
    }

    async openTaxLines(tax) {
        const domain = [
            ["company_id", "=", this.state.companyId],
            ["tax_line_id", "=", tax.id],
            ["date", ">=", this.dateFrom],
            ["date", "<=", this.dateTo],
        ];
        if (this.state.targetMove === "posted") {
            domain.push(["parent_state", "=", "posted"]);
        } else {
            domain.push(["parent_state", "!=", "cancel"]);
        }
        return this.action.doAction({
            type: "ir.actions.act_window",
            name: _t("Tax Journal Items"),
            res_model: "account.move.line",
            views: [[false, "list"], [false, "form"]],
            domain,
            target: "current",
        });
    }

    printReport() {
        window.print();
    }
}

registry.category("actions").add("om_account_accountant.journal_audit", JournalAudit);
