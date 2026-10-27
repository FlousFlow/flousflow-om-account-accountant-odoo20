# Enterprise Accounting Parity Matrix

This is the living gap-analysis baseline for the FlousFlow Community Accounting
Suite. It separates native Community coverage from the remaining Enterprise
parity work; it is not a claim that Community and Enterprise are identical.

Baseline database: `ff_flousflow_om_accountant20_tmp`  
Odoo: 20.0  
Last inventory: 2026-10-27

| Enterprise destination / function | Standard Community or suite support | Actual gap | Proposed solution |
| --- | --- | --- | --- |
| Balance Sheet | `accounting_pdf_reports` action/menu exists and is installed; wizard exposes report, posted/all entries, comparison, debit/credit, dates and journals | Enterprise full-page interactive toolbar and drill-down behavior are not yet equivalent; currency selector is not present | Keep the verified wizard controls, add parity gaps only after report-engine validation |
| Profit and Loss | `accounting_pdf_reports` action/menu exists and is installed; wizard exposes report, posted/all entries, comparison, debit/credit, dates and journals | Same visual/interaction parity gap as Balance Sheet; currency selector is not present | Reproduce verified date, comparison, status, currency, print and drill-down behavior |
| Cash Flow Statement | `accounting_pdf_reports` action/menu exists and is installed | Enterprise layout and interaction parity not fully verified | Reconcile report lines, filters and export behavior |
| Annual Report | `accounting_pdf_reports` and suite annual-report menu exist | Enterprise template/configuration behavior needs runtime comparison | Test template setup, period selection and output |
| General Ledger | Suite exposes General Ledger under Audit Reports | Enterprise full-page search/grouping/drill-down behavior needs comparison | Preserve native report engine; add targeted UI gaps only |
| Trial Balance | Suite exposes Trial Balance under Audit Reports | Enterprise filters and column behavior need comparison | Add missing filters/columns after evidence |
| Journal Audit | Suite exposes Journals Audit | Enterprise action and result columns need comparison | Compare action payload and result view |
| Partner Ledger and Aged Partner reports | Partner Ledger, Aged Partner Balance, Aged Receivable and Aged Payable are installed | Enterprise interaction and export parity needs runtime proof | Validate filters, partner drill-down and exports |
| Tax Report | Tax Report menu/action is installed | Enterprise localization and period-lock behavior needs comparison | Reuse native tax engine; close verified gaps only |
| Daily reports | Day Book, Cash Book and Bank Book are installed | Enterprise grouping and export behavior needs comparison | Compare output and filters |
| Reconciliation | Bank Reconciliation, Open Items and Match Journal Items are installed | Enterprise reconciliation UX is not yet proven equivalent | Run representative reconciliation flows and document deltas |
| Follow-ups | Follow-ups, My Follow-ups, Send All Reminders and analysis are installed | Enterprise automation/escalation parity needs workflow proof | Test reminders, plans, posting and permissions |
| Assets and depreciation | Assets, Asset Analysis and Depreciation Schedule are installed | Enterprise lifecycle and report UI parity needs comparison | Test acquisition, depreciation, disposal and reporting |
| Budgets | Budgets, Budget Analysis and Budgetary Positions are installed | Enterprise workflow/approval and analysis parity needs comparison | Compare budget lifecycle and analytic integration |
| Cash Forecast | Cash Forecast menu/action is installed | Enterprise forecast inputs and visualization need comparison | Test forecast lines, dashboard and exports |
| Internal Transfers | `ff_account_transfer` is installed and integrated | Enterprise paired-transfer UX and edge cases need comparison | Test bank/cash, multi-company, cancellation and reconciliation |
| Branch analytic accounting | `flousflow_branch_analytic` is installed and integrated | Enterprise analytic distribution and branch P&L parity needs runtime scenarios | Test invoice, sales, POS, stock valuation and enforcement settings |

## Current verified inventory

The database currently has the following integrated modules installed:

- `om_account_accountant` `20.0.1.4.0`
- `ff_account_transfer` `20.0.1.0.0`
- `flousflow_branch_analytic` `20.0.1.0.0`

The next implementation tranche is the report-interaction audit: capture the
Enterprise controls and compare them with the corresponding Community action,
view, report engine and export before changing code.

## Verified parity increment

All common PDF report wizards now calculate a draft-entry count using the
selected company, journals and period.  When the report is set to posted
entries, the form shows an informational warning matching the Enterprise
behavior; it does not change the report scope or posting rules.  The behavior
was upgraded and exercised on `ff_flousflow_om_accountant20_tmp` with one
committed draft journal entry (`draft_entry_count = 1`) and with no draft entry
(`draft_entry_count = 0`).
