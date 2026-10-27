# Enterprise Accounting Parity Matrix

This is the living gap-analysis baseline for the FlousFlow Community Accounting
Suite. It separates native Community coverage from the remaining Enterprise
parity work; it is not a claim that Community and Enterprise are identical.

Baseline database: `ff_flousflow_om_accountant20_tmp`  
Odoo: 20.0  
Last inventory: 2026-10-27

| Enterprise destination / function | Standard Community or suite support | Actual gap | Proposed solution |
| --- | --- | --- | --- |
| Balance Sheet | `accounting_pdf_reports` action/menu exists and is installed; wizard exposes report, posted/all entries, comparison, debit/credit, dates and journals; interactive screen now exposes As of, entry basis, table rows and account links | Enterprise still has richer toolbar controls, currency selector and journal-item drill-down | Extend the interactive screen with comparison, currency and journal-item drill-down |
| Profit and Loss | `accounting_pdf_reports` action/menu exists and is installed; wizard exposes report, posted/all entries, comparison, debit/credit, dates and journals | Same visual/interaction parity gap as Balance Sheet; currency selector is not present | Reproduce verified date, comparison, status, currency, print and drill-down behavior |
| Cash Flow Statement | `accounting_pdf_reports` action/menu exists and is installed | Enterprise layout and interaction parity not fully verified | Reconcile report lines, filters and export behavior |
| Annual Report | `accounting_pdf_reports` and suite annual-report menu exist | Enterprise template/configuration behavior needs runtime comparison | Test template setup, period selection and output |
| General Ledger | Suite exposes General Ledger under Reporting > Ledgers | Enterprise full-page search/grouping/drill-down behavior needs comparison | Preserve native report engine; add targeted UI gaps only |
| Trial Balance | Suite exposes Trial Balance under Reporting > Ledgers | Enterprise filters and column behavior need comparison | Add missing filters/columns after evidence |
| Journal Audit | Suite exposes Journals Audit | Enterprise action and result columns need comparison | Compare action payload and result view |
| Partner Ledger and Aged Partner reports | Partner Ledger, Aged Partner Balance, Aged Receivable and Aged Payable are installed | Enterprise interaction and export parity needs runtime proof | Validate filters, partner drill-down and exports |
| Tax Report | Tax Report menu/action is installed | Enterprise localization and period-lock behavior needs comparison | Reuse native tax engine; close verified gaps only |
| Daily reports | Day Book, Cash Book and Bank Book are installed | Enterprise grouping and export behavior needs comparison | Compare output and filters |
| Reconciliation | Bank Reconciliation, Open Items and Match Journal Items are installed | Enterprise reconciliation UX is not yet proven equivalent | Run representative reconciliation flows and document deltas |
| Follow-ups | Follow-ups, My Follow-ups, Send All Reminders and analysis are installed | Enterprise automation/escalation parity needs workflow proof | Test reminders, plans, posting and permissions |
| Assets and depreciation | Assets and Asset Analysis are installed; Depreciation Schedule is under Statement Reports | Enterprise lifecycle and report UI parity needs comparison | Test acquisition, depreciation, disposal and reporting |
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

## Live UI comparison captured on 2026-10-27

The same Accounting > Reporting > Balance Sheet destination was opened in the
Enterprise database and in the local suite:

| Surface | Enterprise observed behavior | Local suite observed behavior | Status |
| --- | --- | --- | --- |
| Report shell | Full-page report at `/odoo/balance-sheet` with a table | Modal `accounting.report` form | Gap confirmed |
| Date | `As of` toolbar control | Start Date / End Date fields | Partial: date input exists, shell differs |
| Comparison | Dedicated toolbar menu | Enable Comparison plus comparison fields in the wizard | Partial |
| Posting basis | Posted Entries, Accrual Basis toolbar control | All Posted Entries / All Entries radio | Partial: accrual basis is not exposed as a toolbar option |
| Currency | Currency selector (`In $`) | Company currency is implicit | Gap confirmed |
| Draft warning | Link to unposted Journal Entries | Draft count is computed and displayed by the common wizard when applicable | Backend parity added; presentation still differs |
| Report lines | Expandable hierarchy with links on amounts and accounts | PDF output after Print | Gap confirmed: interactive drill-down is missing |
| Print | Toolbar Print button | Wizard Print button | Function exists, location differs |

The Enterprise menu also exposes `Customer Statement`, `Fiscal Report`,
`Executive Summary` and `Loans Analysis`, while the local suite exposes
`Annual Report`, daily books, budget/asset analysis and cash forecast under
Reporting. These are menu-placement and coverage differences to resolve
individually; they are not being treated as interchangeable merely because
both systems have a Reporting menu.

## Verified navigation alignment increment — 2026-10-27

The Enterprise Reporting menu was reopened in the live browser. It orders
Trial Balance before General Ledger under `Ledgers`, and places Depreciation
Schedule last under `Statement Reports`. The local module definitions now use
the same parents and order, with the local-only Annual Report after
Depreciation Schedule. In the local suite, the former `Ledgers` shortcut under
Accounting has been renamed `Grouped Journal Items`, since its actions open grouped
`account.move.line` list/pivot/graph views rather than ledger reports. The
`Journals Audit` destination remains in the additional `Audit Reports` folder.
The local database `ff_flousflow_om_accountant20_tmp` was upgraded for
`accounting_pdf_reports` and `om_account_asset`; the Reporting tree was then
observed in the local UI with the aligned placements.

This is navigation parity only. General Ledger and Trial Balance still open
Community report wizards, while Enterprise's report destinations use an
interactive report interface. Enterprise also has a distinct interactive
Customer Statement with period, account, partner, posting-state and currency
filters; the local Partner Ledger is a different wizard and is not a verified
equivalent. Those behavioral gaps remain open.

## Implemented interactive tranche

The local Balance Sheet (and the shared Profit and Loss report action) now has
an **View Interactive** button. It opens an authenticated server-rendered
screen with an `As of` date, `From` date, Posted/All Entries selector, Apply
button, draft-entry warning, report hierarchy and clickable account rows. The
existing PDF wizard and Print action remain available. The screen was opened
through the local browser session and verified with a temporary posted journal
entry; the account row exposed a working Odoo account form link. The temporary
entry was removed after the check.
