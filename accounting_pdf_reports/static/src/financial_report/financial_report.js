/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { formatMonetary } from "@web/views/fields/formatters";
import { standardActionServiceProps } from "@web/webclient/actions/action_plugin";
import { serializeDate } from "@web/core/l10n/dates";
import { Component, onWillStart, proxy, useProps } from "@odoo/owl";

const { DateTime } = luxon;

export class FinancialReport extends Component {
    static template = "accounting_pdf_reports.FinancialReport";
    props = useProps(standardActionServiceProps);

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        const today = DateTime.now();
        const isProfitLoss = String(this.props.action.context?.report_id) === String(
            this.props.action.context?.profit_loss_report_id
        );
        this.state = proxy({
            reportId: this.props.action.context?.report_id,
            printActionXmlid: this.props.action.context?.print_action_xmlid,
            title: "",
            dateFrom: isProfitLoss ? serializeDate(today.startOf("year")) : "",
            dateTo: serializeDate(today),
            targetMove: "posted",
            comparison: false,
            comparisonContext: false,
            debitCredit: false,
            scale: "unit",
            loading: true,
            lines: [],
            journals: [],
            journalIds: false,
            expanded: [],
            hideZero: false,
            draftCount: 0,
            dismissedDraftWarning: false,
            currencyId: false,
            companyId: false,
            companyName: "",
            formulaInfoKey: null,
        });
        onWillStart(() => this.loadReport());
    }

    get visibleLines() {
        const visible = [];
        const parents = [];
        for (const line of this.state.lines) {
            if (this.state.hideZero && this.isZeroDetail(line) && !this.hasNonzeroChildren(line)) {
                continue;
            }
            while (parents.length && parents[parents.length - 1].level >= line.level) {
                parents.pop();
            }
            const hidden = parents.some((parent) =>
                this.hasChildren(parent) && !this.state.expanded.includes(this.expansionKey(parent))
            );
            if (!hidden) {
                visible.push(line);
            }
            if (this.hasChildren(line)) {
                parents.push(line);
            }
        }
        return visible;
    }

    isZeroDetail(line) {
        return ["account", "category"].includes(line.type) &&
            Math.abs(line.balance || 0) < 0.005 &&
            Math.abs(line.debit || 0) < 0.005 &&
            Math.abs(line.credit || 0) < 0.005 &&
            Math.abs(line.balance_cmp || 0) < 0.005;
    }

    hasNonzeroChildren(line) {
        const index = this.state.lines.indexOf(line);
        for (const child of this.state.lines.slice(index + 1)) {
            if (child.level <= line.level) {
                break;
            }
            if (!this.isZeroDetail(child)) {
                return true;
            }
        }
        return false;
    }

    hasChildren(line) {
        if (!["report", "group", "category"].includes(line.type)) {
            return false;
        }
        const index = this.state.lines.indexOf(line);
        return this.state.lines.slice(index + 1).some((item) => item.level > line.level);
    }

    expansionKey(line) {
        return line.row_key || line.report_id;
    }

    async loadReport() {
        this.state.loading = true;
        try {
            const data = await this.orm.call(
                "report.accounting_pdf_reports.report_financial",
                "get_interactive_data",
                [this.state.reportId, this.state.dateFrom || false, this.state.dateTo,
                    this.state.targetMove, this.state.journalIds, this.state.comparison,
                    this.state.debitCredit]
            );
            this.state.title = data.name;
            this.state.lines = data.lines;
            this.state.comparisonContext = data.comparison_context || false;
            this.state.expanded = [...data.expanded_report_ids, ...data.expanded_group_keys];
            this.state.journals = data.journals;
            if (this.state.journalIds === false) {
                this.state.journalIds = data.journal_ids;
            }
            this.state.draftCount = data.draft_count;
            this.state.currencyId = data.currency_id;
            this.state.companyId = data.company_id;
            this.state.companyName = data.company_name;
            this.state.dismissedDraftWarning = false;
        } catch (error) {
            this.notification.add(error.message || _t("The report could not be loaded."), {
                type: "danger",
            });
        } finally {
            this.state.loading = false;
        }
    }

    onDateChange(field, event) {
        this.state[field] = event.target.value;
        return this.loadReport();
    }

    onJournalsChange(event) {
        this.state.journalIds = Array.from(event.target.selectedOptions, (option) => Number(option.value));
        return this.loadReport();
    }

    toggleLine(line) {
        const key = this.expansionKey(line);
        this.state.expanded = this.state.expanded.includes(key)
            ? this.state.expanded.filter((id) => id !== key)
            : [...this.state.expanded, key];
    }

    formulaInfoKey(line) {
        return line.row_key || `report-${line.report_id || line.name}`;
    }

    toggleFormulaInfo(line) {
        const key = this.formulaInfoKey(line);
        this.state.formulaInfoKey = this.state.formulaInfoKey === key ? null : key;
    }

    toggleAllLines() {
        const expandable = this.state.lines.filter((line) => this.hasChildren(line));
        const allExpanded = this.areAllLinesExpanded();
        this.state.expanded = allExpanded ? [] : expandable.map((line) => this.expansionKey(line));
    }

    areAllLinesExpanded() {
        const expandable = this.state.lines.filter((line) => this.hasChildren(line));
        return expandable.length > 0 && expandable.every((line) =>
            this.state.expanded.includes(this.expansionKey(line))
        );
    }

    formatAmount(value) {
        const scales = {
            unit: { divisor: 1, digits: [69, 2], suffix: "" },
            rounded: { divisor: 1, digits: [69, 0], suffix: "" },
            thousand: { divisor: 1000, digits: [69, 2], suffix: "k" },
            million: { divisor: 1000000, digits: [69, 2], suffix: "M" },
        };
        const scale = scales[this.state.scale];
        return `${formatMonetary((value || 0) / scale.divisor, {
            currencyId: this.state.currencyId,
            digits: scale.digits,
        })}${scale.suffix}`;
    }

    async openLineDetails(line) {
        const accountIds = line.account_ids || (line.account_id ? [line.account_id] : []);
        if (!accountIds.length) {
            return;
        }
        const action = await this.action.loadAction("account.action_account_moves_all");
        const dateFrom = line.detail_date_from ?? this.state.dateFrom;
        const dateTo = line.detail_date_to ?? this.state.dateTo;
        action.domain = [...(action.domain || []), ["account_id", "in", accountIds], ["date", "<=", dateTo]];
        if (dateFrom) {
            action.domain.push(["date", ">=", dateFrom]);
        }
        action.domain.push(["company_id", "child_of", this.state.companyId]);
        if (Array.isArray(this.state.journalIds)) {
            action.domain.push(["journal_id", "in", this.state.journalIds]);
        }
        return this.action.doAction(action);
    }

    async openAccount(accountId) {
        return this.openLineDetails({ account_id: accountId });
    }

    async openPrintOptions() {
        const action = await this.action.loadAction(this.state.printActionXmlid);
        action.context = {
            ...action.context,
            default_date_from: this.state.dateFrom || false,
            default_date_to: this.state.dateTo,
            default_target_move: this.state.targetMove,
            default_journal_ids: this.state.journalIds,
            default_enable_filter: this.state.comparison,
            default_debit_credit: this.state.debitCredit,
        };
        return this.action.doAction(action);
    }

    async exportXlsx() {
        try {
            const comparisonContext = this.state.comparisonContext || {};
            const wizardIds = await this.orm.create("accounting.report", [{
                account_report_id: this.state.reportId,
                company_id: this.state.companyId,
                date_from: this.state.dateFrom || false,
                date_to: this.state.dateTo,
                journal_ids: [[6, 0, this.state.journalIds || []]],
                target_move: this.state.targetMove,
                enable_filter: this.state.comparison,
                label_filter: _t("Previous Period"),
                filter_cmp: this.state.comparison ? "filter_date" : "filter_no",
                date_from_cmp: comparisonContext.date_from || false,
                date_to_cmp: comparisonContext.date_to || false,
                debit_credit: this.state.debitCredit,
            }]);
            const action = await this.orm.call(
                "accounting.report", "action_export_xlsx", [[wizardIds[0]]]
            );
            return this.action.doAction(action);
        } catch (error) {
            this.notification.add(error.message || _t("The Excel report could not be exported."), {
                type: "danger",
            });
        }
    }

    async printReport() {
        return this.openPrintOptions();
    }
}

registry.category("actions").add("accounting_pdf_reports.financial_report", FinancialReport);
