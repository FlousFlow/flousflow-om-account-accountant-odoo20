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
            year: DateTime.now().year,
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
        onWillStart(() => this.loadReport());
    }

    get dateFrom() {
        return `${this.state.year}-01-01`;
    }

    get dateTo() {
        return `${this.state.year}-12-31`;
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

    async onYearChange(ev) {
        const year = Number.parseInt(ev.target.value, 10);
        if (!Number.isInteger(year) || year < 1900 || year > 9999) {
            return;
        }
        this.state.year = year;
        await this.loadReport();
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
