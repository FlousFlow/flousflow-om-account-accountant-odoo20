/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { formatMonetary } from "@web/views/fields/formatters";
import { standardActionServiceProps } from "@web/webclient/actions/action_plugin";
import { Component, onWillStart, proxy, useProps } from "@odoo/owl";

const { DateTime } = luxon;

export class DeferredScheduleReport extends Component {
    static template = "om_account_accountant.DeferredScheduleReport";
    props = useProps(standardActionServiceProps);

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        const params = this.props.action.params || {};
        this.state = proxy({
            reportType: params.report_type || "expense",
            period: DateTime.now().toFormat("yyyy-MM"),
            groupBy: "account",
            targetMove: "posted",
            comparisonPeriods: 0,
            comparisonMode: "percentage",
            sortOrder: "desc",
            hideZero: false,
            scale: 1,
            settingsOpen: false,
            search: "",
            journals: [],
            journalIds: [],
            journalPickerOpen: false,
            loading: true,
            companyName: "",
            currencyId: false,
            periods: [],
            rows: [],
        });
        onWillStart(() => this.loadReport());
    }

    get title() {
        return this.state.reportType === "expense" ? _t("Deferred Expenses") : _t("Deferred Revenues");
    }

    get totals() {
        return this.visibleRows.reduce((result, row) => ({
            entries: result.entries + row.entries,
            amount: result.amount + row.amount,
        }), { entries: 0, amount: 0 });
    }

    get visibleRows() {
        const search = this.state.search.trim().toLocaleLowerCase();
        if (!search) {
            return this.state.rows;
        }
        return this.state.rows.filter((row) => row.name.toLocaleLowerCase().includes(search));
    }

    async loadReport() {
        this.state.loading = true;
        try {
            const data = await this.orm.call(
                "account.deferred.schedule.report",
                "get_report_data",
                [this.state.reportType, this.state.period, this.state.groupBy,
                    this.state.targetMove, this.state.comparisonPeriods > 0, this.state.hideZero,
                    this.state.journalIds, this.state.comparisonPeriods,
                    this.state.comparisonMode, this.state.sortOrder]
            );
            this.state.companyName = data.company_name;
            this.state.currencyId = data.currency_id;
            this.state.rows = data.rows;
            this.state.journals = data.journals;
            this.state.periods = data.periods;
        } catch (error) {
            this.notification.add(error.message || _t("The deferred report could not be loaded."), {
                type: "danger",
                sticky: true,
            });
            this.state.rows = [];
        } finally {
            this.state.loading = false;
        }
    }

    async onFilterChange(key, value) {
        this.state[key] = value;
        await this.loadReport();
    }

    onScaleChange(ev) {
        this.state.scale = Number(ev.target.value) || 1;
    }

    async onComparisonToggle(ev) {
        await this.onFilterChange(
            "comparisonPeriods",
            ev.target.value === "previous" ? Math.max(this.state.comparisonPeriods, 1) : 0
        );
    }

    async onComparisonPeriodCount(ev) {
        await this.onFilterChange("comparisonPeriods", Number(ev.target.value) || 1);
    }

    async onComparisonOptionChange(key, ev) {
        await this.onFilterChange(key, ev.target.value);
    }

    comparisonValue(row, periodKey) {
        return row.comparison_values[periodKey];
    }

    totalComparisonValue(periodKey) {
        if (this.state.comparisonMode === "percentage") {
            const comparedAmount = this.visibleRows.reduce(
                (total, row) => total + row.period_values[periodKey], 0
            );
            if (comparedAmount === 0) {
                return this.totals.amount === 0 ? 0 : null;
            }
            return ((this.totals.amount - comparedAmount) / Math.abs(comparedAmount)) * 100;
        }
        return this.visibleRows.reduce(
            (total, row) => total + row.comparison_values[periodKey], 0
        );
    }

    formatComparison(value) {
        if (value === null || value === undefined) {
            return "—";
        }
        if (this.state.comparisonMode === "percentage") {
            return `${new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(value)}%`;
        }
        return this.formatAmount(value);
    }

    onSearchInput(ev) {
        this.state.search = ev.target.value;
    }

    toggleJournalPicker() {
        this.state.journalPickerOpen = !this.state.journalPickerOpen;
    }

    isJournalSelected(journalId) {
        return this.state.journalIds.includes(journalId);
    }

    async onJournalToggle(journalId, ev) {
        const ids = new Set(this.state.journalIds);
        if (ev.target.checked) {
            ids.add(journalId);
        } else {
            ids.delete(journalId);
        }
        this.state.journalIds = [...ids];
        await this.loadReport();
    }

    toggleSettings() {
        this.state.settingsOpen = !this.state.settingsOpen;
    }

    exportXlsx() {
        this.state.settingsOpen = false;
        const params = new URLSearchParams({
            report_type: this.state.reportType,
            period: this.state.period,
            group_by: this.state.groupBy,
            target_move: this.state.targetMove,
            compare_previous: this.state.comparisonPeriods > 0 ? "1" : "0",
            comparison_periods: String(this.state.comparisonPeriods),
            comparison_mode: this.state.comparisonMode,
            sort_order: this.state.sortOrder,
            hide_zero: this.state.hideZero ? "1" : "0",
            scale: String(this.state.scale),
            journal_ids: this.state.journalIds.join(","),
        });
        return this.action.doAction({
            type: "ir.actions.act_url",
            url: `/om_account_accountant/deferred_schedule/xlsx?${params.toString()}`,
            target: "download",
        });
    }

    formatAmount(value) {
        return formatMonetary((value || 0) / this.state.scale, { currencyId: this.state.currencyId });
    }

    async openGroup(row, period = this.state.period) {
        try {
            const domain = await this.orm.call(
                "account.deferred.schedule.report",
                "get_group_move_domain",
                [this.state.reportType, period, this.state.groupBy,
                    row.group_id, this.state.targetMove, row.group_model, this.state.journalIds]
            );
            return this.action.doAction({
                type: "ir.actions.act_window",
                name: this.title,
                res_model: "account.move",
                views: [[false, "list"], [false, "form"]],
                domain,
                target: "current",
            });
        } catch (error) {
            this.notification.add(error.message || _t("The selected schedule entries could not be opened."), {
                type: "danger",
            });
        }
    }

    printReport() {
        window.print();
    }
}

registry.category("actions").add("om_account_accountant.deferred_schedule", DeferredScheduleReport);
