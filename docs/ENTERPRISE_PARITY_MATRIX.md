# Enterprise Accounting Parity Matrix

This is the living gap-analysis baseline for the FlousFlow Community Accounting
Suite. It separates native Community coverage from the remaining Enterprise
parity work; it is not a claim that Community and Enterprise are identical.

Baseline database: `flousflow_om_accountant_dev20_20261028`; Odoo 20.0; last inventory: 2026-10-29.

| Enterprise destination / function | Standard Community or suite support | Actual gap | Proposed solution |
| --- | --- | --- | --- |
| Balance Sheet | The menu opens a full-page in-app report with As of date, comparison, posted/all entries, debit/credit columns, journal filters, amount scaling, draft warning, expandable report rows, account-to-journal-item links and Print options | Browser comparison confirms the asset, liability and equity labels/order, plus formula-info icons. Live-value parity is unproven because the databases contain different data | Continue comparing formulas, options, drill-downs and equivalent fixtures |
| Profit and Loss | Full-page report with month, quarter, fiscal-year and custom periods, previous/next period navigation, previous period (N periods), same period last year, custom dates, percentage-of report line, comparison amount/percentage, period-column sorting, entry state, debit/credit, journal filters, scaling and Print options | PDF/XLSX preserve comparison periods/order and the selected Percentage of base line; budget selection, cash/accrual parity and full P&L hierarchy still need direct comparison | Verify local layout and hierarchy; compare budget and cash/accrual behavior |
| Cash Flow Statement | `accounting_pdf_reports` action/menu exists and is installed | Enterprise layout and interaction parity not fully verified | Reconcile report lines, filters and export behavior |
| Annual Report | `accounting_pdf_reports` and suite annual-report menu exist | Enterprise template/configuration behavior needs runtime comparison | Test template setup, period selection and output |
| General Ledger | Interactive full-page report with account search, expandable journal items, month/quarter/fiscal-year/custom dates, posting/cash-basis filters, scaling, Print, XLSX and CSV | Report controls and date presets now align with observed Enterprise behavior. Documents and Knowledge actions remain absent; export output still needs direct live-file comparison | Validate exports against matched records; consider Documents and Knowledge integrations where available |
| Audit Trail | Searchable audit log with Journal Entry, Account, Taxes, Partners, Company, Restricted and Date filters; grouping and export; Enterprise also exposes Spreadsheet and Knowledge actions plus custom-field editing | Review menu destination and filters match locally. Enterprise additionally offers Link/Insert List in Spreadsheet, Insert View/Template in Knowledge, and Studio custom fields; local actions show Export only. Row counts differ because the databases have different audit data | Keep core Review destinations equivalent; consider optional integrations only when compatible apps are installed |
| Trial Balance | Full-page interactive report with opening balance, period debit/credit, ending balance, previous-period comparison, period presets, journal and entry filters, accrual/cash-basis selection, search, scaling, drill-down, and Print | Core table and filters now match the observed Enterprise Trial Balance screen. Export/settings actions and matched live-value comparison remain open | Verify export/settings behavior and reconcile figures on matched entries |
| Journal Audit | Period presets, entry filters, payment toggle, scale, per-journal audit action, tax summary, print, XLSX export, Send to Documents and Insert in Article | Local Community report supports the core report and XLSX. Send to Documents and Insert in Article are absent; Documents is not available in the local addons path and Knowledge is uninstallable in this Community database | Keep the core report independent of Enterprise apps; add these two actions only through a compatible optional-app integration |
| Customer / Vendor Statement and Partner Ledger | Local `accounting_pdf_reports` 2.0.24 has a full-page statement with period presets, trade/non-trade account scopes, partner/tag filters, posted/draft/all entries, scaling, move drill-down and browser Print. Payable amounts now use vendor-positive signs, and the title changes with account scope. Existing Partner Ledger and Follow-Ups remain available. | Focused isolated tests pass, including positive vendor bill balance. The local 8077 route renders and changes to Vendor Statement for payable-only scope. The database has no posted trade partner lines, so Enterprise row values could not be matched. Remaining gaps: Send, native Odoo PDF output, pagination above 10,000 lines, non-trade mapping confirmation and matched row-level comparison. | Compare customer and vendor statements using matched accounting records. Add filtered report send/PDF and pagination. Repair local Odoo PDF rendering and verify print output while preserving the other statement workflows. |
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

- `om_account_accountant` `20.0.1.33.0`
- `accounting_pdf_reports` `20.0.2.0.18`
- `ff_account_transfer` `20.0.1.0.0`
- `flousflow_branch_analytic` `20.0.1.0.0`

The active report-interaction tranche compares each Enterprise destination
with the corresponding Community action, view, report engine and export. The
Balance Sheet and Profit and Loss have initial full-page implementations;
General Ledger and other destinations remain in progress.

## Verified Profit and Loss comparison increment — 2026-10-29

The P&L comparison control now supports no comparison, previous period (with
an adjustable period count), the same period last year, custom comparison
dates, and a percentage-of selected report line. Period comparison displays
current amount, one column per comparison period, and a change (amount or
percentage) column for a single comparison period, matching the live Enterprise
table. Multiple comparison periods sort chronologically ascending or
descending. Percentage changes display N/A when the comparison amount is zero.
Custom ranges are validated server-side.
Print and XLSX use every selected period-comparison range, preserve the
ascending/descending column order, and show the same single-period change amount
or percentage as the interactive report. Percentage-of selection now carries
the selected base line into PDF and XLSX, with the same zero-base behavior as
the interactive report.

The live Enterprise P&L was observed with columns for current period, prior
period, and Change (%). Selecting a percentage-of base line replaces the prior
period column with the percentage-of value; a zero base displays N/A. The local
8077 database was backed up before upgrade and now reports
`accounting_pdf_reports` `20.0.2.0.18`. Runtime smoke checks on 2.0.15 verified
previous-period, multi-period quarter, same-year and custom date ranges, plus
percentage-of mode disabling period-comparison aggregation. Version 2.0.16 was
upgraded successfully and its regenerated browser asset includes the Balance
Sheet-safe chronological sort fallback. Version 2.0.17 adds the same selected
comparison periods and ordering to PDF and XLSX output. A two-period query
returned two comparison contexts and two distinct comparison values on each
report line. Version 2.0.18 preserves Percentage of base selection in PDF and
XLSX. The local HTTP
login endpoint returned 200. The live Enterprise ascending selection was
observed ordering periods oldest-to-newest; the local interface now sorts its
period columns the same way. The local browser session is active again and the
Review menu and Audit Trail page were rechecked on 2026-10-29. Budget selection,
cash/accrual parity and full P&L hierarchy remain open gaps.

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

This is navigation parity only. General Ledger opens the suite's interactive
report; Trial Balance still opens the Community report wizard, while
Enterprise's report destinations use an interactive report interface.
Enterprise has a distinct interactive Customer Statement with period, account
(including non-trade receivable/payable), partner/tag, posting-state and currency
filters. Its table shows date, due date, amount and transaction-currency amount,
and the report offers Print and Send. Local `accounting_pdf_reports` 2.0.24 now
adds a dedicated interactive Customer / Vendor Statement route with the core
filters and move drill-down, while retaining the separate Partner Ledger wizard
and Follow-Ups PDF/XLSX/email actions. Local Print currently uses the browser's
print function; Send and full PDF output are still open. The local development
database has no posted partner journal lines, and the live Enterprise report
was empty for the observed scope, so row-level values remain unverified. The
legacy Partner Ledger still reports a missing Odoo PDF engine and falls back
to HTML; that runtime issue is tracked separately.

## Verified Review menu increment — 2026-10-28

The live Enterprise Review > Control menu exposes **Journal Items**, **Audit
Trail**, and **Journal Audit** in that order. The local suite had **Entries to
Review** first, which is a different `account.move` queue and does not match
Enterprise's posted `account.move.line` destination at `/odoo/items`. The
native Journal Items action is now also linked from Review > Control, ahead of
the existing suite-specific Entries to Review queue. The extra queue remains
available after the three Enterprise destinations. This closes the menu/action
gap without removing existing functionality. Odoo menu tests passed, including
the entire ordered Review group tree, the native `account.move.line` action,
and visibility for an accounting user.

The live Enterprise **Journal Audit** date menu also exposes Month, Quarter,
Fiscal Year, and Custom Dates, with previous/next controls for each period.
The local report previously supported only a numeric calendar year. Its date
filter now supports the same period types and navigation; Fiscal Year bounds
come from the active company's configured fiscal-year settings. Custom date
ranges validate start/end order before reloading the report. A local Odoo browser
tour exercised Month, Quarter, next-quarter navigation, Fiscal Year, and custom
date entry on 2026-10-28; the fiscal-year unit tests and full Review menu-tree
tests passed in the same run (0 failures across 14 tests). The test also exposed and fixed
eager loading of the Spreadsheet editor's dependencies on unrelated accounting
pages; the editor now loads its bundle only when a working-file spreadsheet is
opened.

## Implemented interactive tranche

The local Balance Sheet menu now opens an in-app client action directly,
without first showing the report wizard. Profit and Loss uses the same report
shell and the code now opens with the company's full fiscal year. Its period selector provides
Month, Quarter, Fiscal Year and Custom Dates, with previous/next navigation for
the standard periods. Fiscal-year boundaries come from Odoo's company settings,
and comparison periods follow the selected fiscal year or immediately preceding
range. Balance Sheet retains its `As of` control. Both reports provide
Comparison, Posted/All Entries, debit/credit columns, journal selection, amount
scaling, draft warning and Print options. The account report engine remains the
source of report values, and account rows link to journal items. Balance Sheet
now groups account types under current assets and liabilities, shows fixed and
non-current asset categories, and calculates section/category totals. The
visible labels for Bank and Cash Accounts and Receivables match Enterprise in
English and have Arabic translations. The existing print wizard is still
available from Print and the settings control.

The updated `ff_flousflow_om_accountant20_tmp` database was verified in the
local browser on 2026-10-28 before the latest hierarchy refinement: Balance
Sheet and Profit and Loss both opened directly; Comparison added a
previous-period column; debit/credit toggled its columns; and Print opened the
existing wizard. The local database showed zero balances at the selected date,
so this did not establish numerical equivalence with Enterprise, whose
displayed Payables figure came from its own database. The latest code groups
account-type lines under Current Assets and Current Liabilities, adds fixed and
non-current asset categories, and calculates category and section subtotals
from the financial-report engine. Its Odoo module tests pass; the revised
hierarchy still needs a fresh browser check. Enterprise settings and full
drill-down parity remain open gaps.

## Verified Balance Sheet hierarchy increment — 2026-10-28

The local browser and live Enterprise report were compared again. Both show
Current Assets followed by Bank and Cash Accounts, Receivables, Current Assets,
Prepayments and Total Current Assets; both then show Fixed Assets,
Non-current Assets and Total ASSETS. The current-liability category is named
Current Liabilities in both. The equity section also matches Enterprise's
Capital, Earnings, Current Year Unallocated Earnings, Previous Years Earnings,
Total Earnings, Total EQUITY (& EARNINGS), and LIABILITIES + EQUITY rows. The
local report had called the categories Other Current Assets,
Other Current Liabilities and Equity. Those labels now match Enterprise while
retaining the same account type domains and totals. The Balance Sheet test
asserts the corrected names; all 10 `TestBalanceSheet` tests passed on
`flousflow_om_accountant_dev20_20261028` after upgrading
`accounting_pdf_reports`. The database was backed up before the upgrade.

This closes the observed hierarchy and category-label differences only.
Formula parity beyond inspected info popovers, all report options and drill-down
parity remain part of the ongoing comparison; live-value parity remains
unproven because the Enterprise and local databases contain different data.

## Verified Journal Audit action increment — 2026-10-28

The same Journal Audit destination was inspected in Enterprise and the local
suite. Enterprise keeps the per-journal Audit action visible even when the
To Review count is zero. The local report previously hid that action in this
case. It now remains visible to accounting users; its server-side handler still
marks only posted entries in the selected company, journal and period, and
returns zero without changing anything when none are pending. Read-only users
do not receive the action. The browser tour checks the zero-pending case when a
matching journal row exists, and the local browser showed Audit beside
Miscellaneous Operations with a count of zero after the upgrade. The Journal
Audit period tour, period tests and Review menu tests passed together
(0 failures across 8 selected tests).

Review > Control still matches Enterprise's three destinations and their order;
the local-only Entries to Review queue remains afterward as an additional
destination. Export integrations and the Enterprise workflow behind the
separate tax verification link remain open parity items.

## Verified General Ledger export and period increment — 2026-10-29

The Enterprise General Ledger options menu exposes XLSX, CSV, Send to
Documents, and Insert in Article. The local interactive report already matches
the observed account summary, expandable move rows, posted/draft and
cash-basis controls, amount scale, Print, and Journal Items drill-down. The
period picker supports month, quarter, company fiscal year, and custom dates;
these resolved date boundaries are shared by the on-screen report, print,
exports, and Journal Items drill-down. Its settings menu now offers XLSX and
CSV. Both endpoints preserve the selected
period, entry state, cash-basis option, amount scale, and account search; XLSX
contains General Ledger and Journal Items worksheets, while CSV includes
account totals and journal-item rows. An Odoo HTTP test validates both response
formats, and a browser tour checks the report's export menu. The report tour
also exposed and fixed a QWeb render error when collapsed account rows had not
loaded move details.

Documents and Knowledge are still unavailable in the local Community addons
path. Export file values and layout still need comparison against live
Enterprise exports using matched company data.

## Verified Trial Balance interactive increment — 2026-10-29

The live Enterprise Trial Balance opens as a full-page report with opening
balance, selected-period debit and credit, ending balance, previous-period
comparison, Month/Quarter/Fiscal Year/Custom Dates, posted/all-entry basis,
journal selection, amount scaling, search, drill-down links, and Print. The
local Trial Balance menu now opens an interactive report with the same table
structure and controls. Opening amounts are calculated from entries before the
selected period; period and closing values use the existing Trial Balance SQL
engine and remain company/journal scoped. The original report wizard stays
available through Print and the account report action.

Tests verify opening/current/comparison amounts against posted invoices,
debit-credit reconciliation, menu permissions, period controls, and rendered
comparison columns. Cash Basis Method is available in the filter and print
wizard and uses the tax-exigibility context consistently with General Ledger.
The local test browser completed the period, comparison, and entry-basis tour.
Enterprise export/settings actions and numeric equivalence across the two
databases are still unverified.

## Verified Review and Journal Audit recheck — 2026-10-29

The live Enterprise Review drawer was inspected from the accounting app. Its
tree is Control (Journal Items, Audit Trail, Journal Audit), Audit (Working
Files, Annual Report), Inventory (Inventory Valuation), Regulatory (Unrealized
Currencies, Deferred Revenues, Deferred Expenses), Purchases (Bills To Receive,
Billed Not Received), and Sales (Invoices To Be Issued, Invoiced Not Delivered).
The local 8077 database was queried by external menu ID, parent, sequence and
action. Control and the other Review groups matched, but Inventory Valuation
was directly under Review locally while Enterprise nests it under Inventory.
The local menu now reuses the Inventory folder and nests Inventory Valuation
inside it. Work Queues and Reconciliation remain under Accounting entries, so
they do not add destinations to Review. The Review menu tests passed (0 failures)
after the upgrade, and the 8077 database now reports `om_account_accountant`
`20.0.1.33.0` installed with the matching parent/child menu records.

The Enterprise Journal Audit report exposes Documents, To Review, Debit,
Credit and Balance; its filters include period, posted/draft/all entries and
Include Payments. Its Tax Summary has an Audit link that opens Taxes Applied,
grouped by tax and account. The local report implements the same core filters,
table, tax summary and grouped account.move.line action with company, period,
posting state and payment scope. The Enterprise settings menu additionally
shows XLSX, Send to Documents and Insert in Article; the local menu currently
shows XLSX only because the compatible Documents and Knowledge apps are not
available in this Community runtime.

The Enterprise report showed three documents and $10,031.50 in October 2026;
the local 8077 database has one posted move and zero debit/credit for that
period. These are different datasets, so matching report structure does not
establish numeric parity.


## Live Review parity recheck — 2026-10-29

Enterprise and local Review menus expose the same ordered groups and entries: Control (Journal Items, Audit Trail, Journal Audit), Audit (Working Files, Annual Report), Inventory (Inventory Valuation), Regulatory (Unrealized Currencies, Deferred Revenues, Deferred Expenses), Purchases (Bills To Receive, Billed Not Received), and Sales (Invoices To Be Issued, Invoiced Not Delivered). No Review destination is missing in the current local database.

The Audit Trail list also exposes the same core filter and grouping choices locally: Journal Entry, Account, Taxes, Partners, Company, Restricted, Date, Date grouping, Custom Group, and Favorites. The live Enterprise action menu additionally shows Link List in Spreadsheet, Insert List in Spreadsheet, Insert View in Article, and Insert Template in Article. Enterprise's column menu has Add Custom Field; local Odoo has no `web_studio` module. These are Enterprise Spreadsheet/Knowledge/Studio integrations, not missing core Review destinations. The Community database has `spreadsheet` installed but `can_insert_in_spreadsheet` remains false, and Knowledge is uninstallable. Preserve compatibility by treating these as optional integrations; do not make the accounting suite depend on unavailable Enterprise modules. Audit row totals differ (local 5, Enterprise 182) and cannot be compared as the databases contain different records.
