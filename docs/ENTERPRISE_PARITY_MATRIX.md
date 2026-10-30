# Enterprise Accounting Parity Matrix

This is the living gap-analysis baseline for the FlousFlow Community Accounting
Suite. It separates native Community coverage from the remaining Enterprise
parity work; it is not a claim that Community and Enterprise are identical.

Baseline database: `flousflow_om_accountant_dev20_20261028`; Odoo 20.0; last inventory: 2026-10-30.

| Enterprise destination / function | Standard Community or suite support | Actual gap | Proposed solution |
| --- | --- | --- | --- |
| Balance Sheet | The menu opens a full-page in-app report with As of date, comparison, posted/all entries, debit/credit columns, journal filters, amount scaling, draft warning, expandable report rows, account-to-journal-item links and Print options. Formula-info icons expose Engine, Label, Formula and Value. | Local `accounting_pdf_reports` `2.0.72` is installed. Browser tours verify Current Assets formula `BA.balance + REC.balance + CAS.balance + PRE.balance`, unscaled two-decimal value, Total ASSETS formula `CA.balance + FA.balance + PNCA.balance`, and XLSX export returning to the report. | The latest verification used browser tours, not the user's authenticated local session. A nonzero formula popover at `k$` and matched-data numeric parity remain open. | Sign in locally to inspect the nonzero `k$` popover; compare additional formula types, report options, drill-downs and equivalent fixtures |
| Profit and Loss | Enterprise displays Revenue, Cost of Revenue, Gross Profit, Operating Expenses, Operating Income (or Loss), Other Income, Other Expenses, Net Income and Distributions/Withdrawals, with formula details for each; Revenue uses the income domain with `-sum`, Gross Profit is `REV.balance - COS.balance`, Operating Income is `REV.balance - COS.balance - EXP.balance`, and Net Income is `REV.balance + OIN.balance - COS.balance - EXP.balance - OEXP.balance`. | Local `accounting_pdf_reports` `2.0.73` builds the same nine flat rows and total styling, retains account/journal-item drill-downs, and calculates the six domain rows and three aggregates from posted balances. Focused unit and browser-tour checks verify order, formulas and populated summary amounts. | Matched-data comparison with Enterprise's configured books, nonzero `k$` tooltip display, and nonzero comparison/budget columns still need verification. Full module demo replay reported existing-state errors in nine modules. | Compare formulas and amounts on matched posted entries, then verify comparison and budget views on data configured in both systems |
| Cash Flow Statement | Live Enterprise `/odoo/cash-flow` shows month/quarter/fiscal-year/custom periods, posted/draft/all plus hide-zero, currency scale, expandable detail, source-line drill-down, Print and XLSX; Documents and Knowledge actions are also present. The table omits company/Description headers and labels investing as “Investing and Extraordinary Activities.” | Local `accounting_pdf_reports` `20.0.2.0.79` retains the same period types, move-state choices, hide-zero, scale, detail and drill-down. On the same displayed September 2026 period, the local engine returns opening 0, net change 2,425, closing 2,425; three posted bank lines (2,000, -850, +1,275) are each against suspense account 101402 and unreconciled. | Enterprise displayed zero opening/net/closing for September 2026, so amounts do not match. These records differ between the databases; the local difference is explained by its three unmatched bank lines and is not yet evidence of a calculation defect. Local keeps an optional journal filter. Documents/Knowledge actions are unavailable in Community. Local browser sign-in expired after upgrade, preventing a fresh visual comparison. | Build a matched cash-entry fixture in both systems; compare reconciliation/classification, PDF and XLSX values, then recheck the local screen after sign-in. |
| Accounting dashboard KPI tiles | The live Enterprise account shows Customer Invoices → Invoice Analysis, Expenses → Profit and Loss, Receivable → Aged Receivable, and Payable → Aged Payable; Setup Your Invoice Layout is also shown. | On local 8077, all four cards were clicked and opened the equivalent routes: Invoice Analysis, Profit and Loss (`action-450`), Aged Receivable (`action-656`), and Aged Payable (`action-657`). Local also shows Cash → Cashflow Analysis. A Cash drag to the first position survived reload; the user's original order was restored and verified in PostgreSQL. | The inspected Enterprise dashboard does not expose a separate Cash KPI, whereas Community currently does. Amounts and personal ordering differ between databases/users. Responsive drag behavior at phone/tablet widths remains unverified. | Keep the Cash KPI as a documented local-only extra; verify drag interaction at phone/tablet widths without resetting the saved user order |
| Aged Receivable / Aged Payable | Enterprise rows show Partner and Open Items actions beside expandable balances, with as-of date, date basis, aging period, posting state and currency scale. | Local actions open Partner and the interactive Open Items report; current-company scope and native residual-at-date behavior are covered by tests. | Local and Enterprise accounting data differ, so balances require matched fixtures. User browser verification is pending after session expiry. | Compare matching open/reconciled items and inspect the rendered action |
| Partner Open Items | Enterprise partner More menu opens an interactive report with filters, No Reminder, currencies, Partner/Journal Items actions, Print, Send and XLSX. Ready Mat showed -$6,936.00. | Local stat button opens the same report functions: native residual-at-date values, responsive layout, unposted warning, native No Reminder inverse, partner/journal drill-downs, existing follow-up wizard, QWeb PDF action/template and RTL XLSX. Ready Mat returns 4 payable lines (-$9,727.62) and 1 draft line. Eleven focused Open Items and Partner Ledger tests pass, including report HTML/template and XLSX checks; the Chrome report tour passed separately. The current unit suite verifies PDF action configuration, not binary PDF rendering. Modules are `accounting_pdf_reports` 2.0.74 and `om_account_accountant` 20.0.1.34.33. | Local and Enterprise totals differ because the databases contain different entries. The user's local browser session expired at service restart. Enterprise Documents/Knowledge actions are unavailable in this Community runtime. | Sign in and inspect Ready Mat; verify a fresh PDF download, compare equivalent fixtures, and review the reminder composer without sending |
| Annual Report | On 2026-10-30 Enterprise showed the setup Kanban; New opened a dialog with title placeholder `Example, Annual Financial Overview FY`, the previous full-year dates (2025), current user as responsible, and the Annual Report template. | Local defaults match the prior calendar year, active user, and template; the form contains the complete-PDF action. `accounting_pdf_reports` `2.0.71` now uses the same title placeholder and Arabic translation. Six focused annual-document tests passed, and the module is installed on 8077. | Local browser is unauthenticated, so local dialog geometry and Arabic translation are not visually confirmed; Arabic language is not enabled in the local database. Knowledge article templates/editor integrations remain unavailable in Community. | Sign in locally to compare the New flow, content editing, and PDF layout; load Arabic language before visually comparing translated labels. |
| General Ledger | Interactive full-page report with account search, expandable journal items, month/quarter/fiscal-year/custom dates, posting/cash-basis filters, scaling, Print, XLSX and CSV | Report controls and date presets now align with observed Enterprise behavior. Documents and Knowledge actions remain absent; export output still needs direct live-file comparison | Validate exports against matched records; consider Documents and Knowledge integrations where available |
| Audit Trail | Live Enterprise screen `/odoo/action-325` shows Date, Author, Name and Description; search filters include Journal Entry, Account, Taxes, Partners, Company, Restricted and Date; grouping includes Date and Updated Data. The current action menu exposes Export and Knowledge → Insert View in Article / Insert Template in Article. The settings menu exposes Add Custom Field. | Local 8077 has the same `mail.message` Audit Trail action, list view and search view installed from Odoo 20 core. Its XML defines the same record types, Restricted/Date filters, Date/Updated Data grouping, and four visible columns. | Local browser is unauthenticated, so UI parity is source/DB-record verified rather than screen verified. This Enterprise user's current menus did not show a Spreadsheet action; earlier notes about Spreadsheet integration need confirmation against the exact account/apps before treating it as a gap. Audit row counts differ with database data. | Verify the local filters/grouping after sign-in; confirm whether Spreadsheet actions are enabled for the relevant Enterprise account and available Community integration before implementing anything. |
| Trial Balance | Full-page interactive report with opening balance, period debit/credit, ending balance, previous-period comparison, period presets, journal and entry filters, accrual/cash-basis selection, search, scaling, drill-down, and Print | Core table and filters now match the observed Enterprise Trial Balance screen. Export/settings actions and matched live-value comparison remain open | Verify export/settings behavior and reconcile figures on matched entries |
| Journal Audit | Live Enterprise report at `/odoo/journal-report` filters by period, posted/draft/all moves, payments and scale. On 2026-10-30, Purchases showed 3 documents and 0 To Review. Expanding a group reveals account totals and its Applied Taxes table; a separate global Tax Summary follows. Its single **Audit** button opens the scoped `account.move.line` list grouped by Journal Entry; settings include XLSX, Send to Documents and Insert in Article. | Local has the same filters and expandable account/tax details. **Audit** opens the scoped Journal Items action with the same Journal Entry grouping enabled. Toolbar matches Enterprise: title without a company label; Print and Report options on the action row; period, target moves, Include Payments and scale visible by default on desktop. A filter toggle controls the row on phone widths. Odoo-native icons are used. Installed manifest version `20.0.1.34.34`; focused Chrome tours passed at desktop and 390×844, including period controls and phone filter collapse/expand. | Matched-database amounts and Enterprise phone/tablet rendering remain unverified. Documents and Knowledge actions are unavailable in Community. | Compare report amounts only with equivalent records and inspect the Enterprise responsive layout at phone/tablet widths. |
| Purchase accrual review queues | Enterprise Review > Purchases has **Bills To Receive** and **Billed Not Received** with an as-of date and vendor grouping. Live `/odoo/action-843` on 2026-10-30 showed Gemini Furniture: 2 records, quantity 25, received 25, billed 0, average unit price 110.75, amount 3,095.00. Its settings menu exposes **Add Custom Field**. | Local XML has matching columns/grouping and `review_accrual_list` as-of control. A read-only 8077 ORM query at 2026-10-30 returned P00005 lines of 20×132.50 and 5×89.00, matching the Enterprise quantity/received/billed/average/amount aggregate exactly. `Billed Not Received` remains empty locally. Local also has a hidden optional Description column. | Data aggregation matches on this fixture. Local screen interaction is still unverified because the browser session is unauthenticated. Enterprise custom-field editing is a Studio capability and is unavailable in this Community runtime; a nonempty Billed Not Received fixture is still needed. | Confirm local rendered controls after sign-in and compare a billed-but-not-received order; keep the Enterprise-only Studio action documented. |
| Sales accrual review queues | Enterprise Review > Sales has **Invoices To Be Issued** and **Invoiced Not Delivered**. On live `/odoo/action-446` at 2026-10-30, Acme Corporation showed 3 lines: quantity 37, delivered 30, invoiced 0, Unit Price sum 23,872, Amount 258,116, Unit Cost sum 4,200. Detail Total Cost was 30,000 + 8,000 + 7,000; the grouped row had no Total Cost subtotal. Invoiced Not Delivered had no rows. | Local defines the same filters/columns and computes per-line Unit Cost and Total Cost. Its view formerly requested grouped Total Cost sums; `sum` was removed from both sales queue Total Cost fields to match Enterprise. Unit Cost grouping and line-level totals remain. Local ORM returned no records for either queue at the same as-of date. | The Enterprise display was verified live. Local amounts cannot be compared because its sales queues are empty and its browser needs sign-in. | Compare with matching sale data; verify local grouped row omits Total Cost subtotal while each detail row retains it. |
| Customer / Vendor Statement | Enterprise shows report period/account/partner/tag/move-state/currency filters, expandable partner balances, detail actions, Print/Send and XLSX in settings; its More menu contains Send; live page opened on September 2026 (previous month). | Local mirrors the report controls and provides XLSX export with active filters and scale; interactive/API/export defaults now use the previous month. On local 8077, Send is in More and `accounting_pdf_reports` is currently installed at `2.0.70`. | Documents/Knowledge integrations are unavailable in Community; XLSX with populated data remains to be compared, and local/Enterprise report rows differ. | Compare export and print values on matching customer/vendor fixtures |
| Aged Receivable / Aged Payable | Full-page interactive reports with as-of date, partner/account/date-basis/period/move-state filters, currency scaling, expandable partner balances and transaction drill-down; aging columns run Not Due, 1-30 through Older, then Total | Local reports now offer the four currency scales in both the interactive view and QWeb print; local empty-data page/zero totals were verified previously. | Matched financial lines are unavailable, so bucket values and drill-down remain unverified. | Compare printed and interactive amounts on matched fixtures |
| Partner Ledger / Customer or Vendor Statement | On live Enterprise `/odoo/accounting/partner-ledger`, filters are Search, fiscal year, Trade Partners account scope, Partners, Posted Entries and currency scale. Columns are Journal, Account, Date, Due Date, Matching, Debit, Credit, Amount Currency and Balance; expandable partners have Partner and Journal Items actions. Expanded journal rows show the move label, journal name and account code, with a per-line More menu → View Journal Entry. The report also has Print, XLSX/Send to Documents/Insert in Article settings and an unposted-entry warning. | Local filters, partner actions and warning remain in source. Detail rows now show move label and journal name plus account code, and provide the same per-line View Journal Entry action; date links now open the actual move record. Focused ledger tests passed (4 tests). The Print wizard has a Document Type selector for Account Statement and Balance Confirmation; this is a FlousFlow addition because Enterprise exposes no confirmation choice. A prior local run generated and visually inspected the Acme confirmation PDF. On 2026-10-30 the local wizard was visible with Balance Confirmation selected; 8077 now returns HTTP 200, the database includes the Odoo demo partners Acme Corporation and Ready Mat, and the user's browser session requires sign-in. | A fresh print after the latest service restart is not verified in the current authenticated session. Local data differs from Enterprise, so totals are not directly comparable. XLSX and warning behavior still need matched records. | Sign in, print the selected confirmation, and compare amounts and XLSX on equivalent partner data. |
| Tax Report | Enterprise has a full-page report with period comparison, target moves, three report layouts (General, Account > Tax, Tax > Account), Net/Tax values, Print and XLSX/Document/Knowledge actions. | Local 8077 now runs `accounting_pdf_reports` `20.0.2.0.79` on the preserved PostgreSQL 17 database clone. It has both grouped layouts, prior-period/same-year/custom comparisons, XLSX grouping and journal-item drill-down. Focused tests passed 14 post-tests with 0 failures/errors; withholding was skipped because its localization is absent. A Chrome tour rendered the report. | Current browser session is logged out, so local screen interaction is not visually confirmed in the user's session. Document/Knowledge actions are unavailable in Community. XLSX was verified through workbook tests, not an authenticated HTTP download; comparison options in PDF need verification. | Sign in locally and compare all three layouts, drill-downs and export on matching tax entries. |
| Daily reports | Day Book, Cash Book and Bank Book are installed | Enterprise grouping and export behavior needs comparison | Compare output and filters |
| Reconciliation | Enterprise `/odoo/reconcile` shows posted entries with residuals, grouped by Account then Partner. Rows show Date, Journal Entry, Description, Currency, Debit, Credit, Matching and Remaining; each group exposes **Auto Reconcile**. | Local Accounting > Reconciliation exposes Bank Reconciliation, Open Items, Match Journal Items and Bank Reconciliation Statement. `Match Journal Items` filters posted, unreconciled lines on reconcilable accounts, grouped by Account and Partner, and opens a manual Match wizard. The duplicate second Reconciliation folder and duplicate shortcuts were deactivated; the unique Transactions to Review shortcut now sits under the original folder. Version `20.0.1.34.35` is installed; all 6 focused `TestMenus` passed. | Local does not yet have the Enterprise residual-group review screen or its per-group Auto Reconcile affordance. Database amounts differ; no reconciliation mutation was run in Enterprise. | Implement and validate equivalent residual-group behavior using isolated fixtures, including partial matches, ambiguous suggestions, and safe auto-reconcile criteria. |
| Follow-ups | Follow-ups, My Follow-ups, Send All Reminders and analysis are installed | Enterprise automation/escalation parity needs workflow proof | Test reminders, plans, posting and permissions |
| Assets and depreciation | Assets and Asset Analysis are installed; Depreciation Schedule is under Statement Reports | Enterprise lifecycle and report UI parity needs comparison | Test acquisition, depreciation, disposal and reporting |
| Budgets | Budgets, Budget Analysis and Budgetary Positions are installed | Enterprise workflow/approval and analysis parity needs comparison | Compare budget lifecycle and analytic integration |
| Cash Forecast | Cash Forecast menu/action is installed | Enterprise forecast inputs and visualization need comparison | Test forecast lines, dashboard and exports |
| Internal Transfers | `ff_account_transfer` is installed and integrated | Enterprise paired-transfer UX and edge cases need comparison | Test bank/cash, multi-company, cancellation and reconciliation |
| Branch analytic accounting | `flousflow_branch_analytic` is installed and integrated | Enterprise analytic distribution and branch P&L parity needs runtime scenarios | Test invoice, sales, POS, stock valuation and enforcement settings |

## Current verified inventory

The database currently has the following integrated modules installed:

- `om_account_accountant` `20.0.1.34.33`
- `accounting_pdf_reports` `20.0.2.0.79`
- `ff_account_transfer` `20.0.1.0.0`
- `flousflow_branch_analytic` `20.0.1.0.0`

The active report-interaction tranche compares each Enterprise destination
with the corresponding Community action, view, report engine and export. The
Balance Sheet and Profit and Loss have initial full-page implementations;
General Ledger and other destinations remain in progress.

## Verified accounting report regression tranche — 2026-10-29

`TestMenuAccess`, `TestCashFlow`, `TestAnnualReportDocument`,
`TestInteractiveCustomerStatement`, and `TestPartnerLedger` passed on
`flousflow_om_accountant_dev20_20261028` after the latest module upgrade
(18 tests, 0 failures, 0 errors). The menu-access test now exercises client
actions through their interactive report services instead of assuming each
destination has a wizard `res_model`. The Accounting app root menu points to
the same 100×100 PNG asset as the module description icon. Local browser UI
confirmation remains pending because the session is at the login page.

The cash-flow print report was aligned to the interactive row order and
fixed group labels; the focused real-entry test verifies the grouped operating
amounts and that all displayed section totals still sum to net change. The
module now explicitly depends on Odoo's `base_report_wkhtmltox` engine addon;
on the normal 8077 runtime, a one-page PDF was generated with patched Qt and
its extracted text confirmed opening balance, net increase, activity rows, and
closing balance in that order.

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
Review menu and Audit Trail page were rechecked on 2026-10-29. Budget selection
still needs direct interaction comparison, and full P&L hierarchy remains an
open gap. Cash Basis Method implementation evidence follows.

## Verified parity increment

### Profit and Loss Cash Basis Method — 2026-10-29

Enterprise's live P&L filter exposes `Cash Basis Method`; selecting it changes
the toolbar to Cash Basis. Local financial reports now use Odoo 20's native
`account.move.line._get_tax_exigible_domain()` through the existing `tax_exigible`
query context. The option applies to interactive report totals, journal-item
drill-downs, print output and XLSX exports, and is retained in comparison
contexts. A transaction test checks that an unpaid invoice with an on-payment
tax is excluded, then reconciles its payment and verifies that generated
cash-basis journal items pass the native filter and report totals agree with the
filtered ledger. PDF and XLSX preserve the selected basis. The focused test
passed on the upgraded 8077 database (one test, zero failures/errors); the local
browser session is unauthenticated, so visual control verification remains open.

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
action. Its current Review tree has the same groups and destinations, including
Inventory Valuation nested inside Inventory. Work Queues and Reconciliation
remain under Accounting entries, so they do not add destinations to Review.
The current installed suite is `om_account_accountant` `20.0.1.34.7`.

The Enterprise Journal Audit report exposes Documents, To Review, Debit,
Credit and Balance; its filters include period, posted/draft/all entries and
Include Payments. Expanded groups show Applied Taxes, followed by the global
Tax Summary; their Audit links open filtered tax journal items. The local report
now implements per-group Applied Taxes and the global summary. Its per-group
drill-down is scoped by journal, document type, company, period, posting state
and payment scope. The Enterprise settings menu additionally
shows XLSX, Send to Documents and Insert in Article; the local menu currently
shows XLSX only because the compatible Documents and Knowledge apps are not
available in this Community runtime.

The Enterprise report showed three documents and $10,031.50 in October 2026;
the local 8077 database has one posted move and zero debit/credit for that
period. These are different datasets, so matching report structure does not
establish numeric parity.


## Live Review parity recheck — 2026-10-29

Enterprise and local Review menus expose the same ordered groups and entries: Control (Journal Items, Audit Trail, Journal Audit), Audit (Working Files, Annual Report), Inventory (Inventory Valuation), Regulatory (Unrealized Currencies, Deferred Revenues, Deferred Expenses), Purchases (Bills To Receive, Billed Not Received), and Sales (Invoices To Be Issued, Invoiced Not Delivered). No Review destination is missing in the current local database.

The Enterprise Working Files checklist exposes four check states: Pending
Review, Reviewed, Supervised, and Exception. On 2026-10-30 its 2025 file showed
18/52 resolved, with the parent header at Reviewed and a separate Certify
action. The live detail page has Cycles, Balances, and Spreadsheet tabs, inline
notes/evidence, reviewer activity, and a manager-facing Certify action. Local
`om_account_accountant` `20.0.1.34.33` implements the same four checklist states,
notes, evidence attachments, and Cycles/Balances/Spreadsheet pages. The live
Enterprise `Audit 2025` checklist currently renders seven **Upload File** actions,
including Accounting Process and Asset Register. Version `20.0.1.34.33` restores
those two template flags and updates linked and legacy checks; it does not delete
attachments. Its Mark
Reviewed action permits pending checks; certification still requires every
check to be resolved, and the older Validate from In Progress action remains
for backward compatibility. This turn added server-side manager enforcement
for setting Supervised through either create or write; the full
`TestWorkingFileBalances` class passed 12 tests on the local 8077 database.
Local demo checklist counts are not equivalent to Enterprise's 2025 record.
Enterprise's certification precondition remains unverified because exercising
it would alter the live audit record. After upgrade `20.0.1.34.33`, the local
Working File screen (`/odoo/action-651/14`) rendered seven **Upload File**
actions, matching the current Enterprise screen. Note autosave and an actual
evidence upload/removal cycle remain unverified.

On 2026-10-30, the live `Audit 2025` detail was re-read without changing it.
Its accessibility tree shows 52 checklist cards in eight sections. A read-only
query of local 8077 confirms 52 active templates and 52 checks in the existing
local working file, with the same per-section counts (16, 4, 9, 3, 2, 5, 8,
5) and seven `evidence_required` items. The seven local upload requirements
match the seven visible Enterprise upload controls. This verifies checklist
structure and upload-flag parity; local check states/notes and Enterprise's
18/52 completion state are intentionally not asserted to match.

The live Enterprise Journal Audit view for 2026 shows the same five columns as
the local client and proceeds from its grouped Journal / document-type rows
directly to the Tax Summary. The local client had added a grand-total row after
the group rows, which Enterprise does not show; that extra row is removed so the
table follows the observed Enterprise layout. Period, target-move, payment and
currency-scale controls also match the currently observed toolbar/filter menus.
The updated `om_account_accountant` version `20.0.1.34.9` was installed on the
local 8077 database; the Journal Audit period/grouping/XLSX test class passed
(4 tests, 0 failures, 0 errors).

The Audit Trail list also exposes the same core filter and grouping choices locally: Journal Entry, Account, Taxes, Partners, Company, Restricted, Date, Date grouping, Custom Group, and Favorites. The live Enterprise action menu additionally shows Link List in Spreadsheet, Insert List in Spreadsheet, Insert View in Article, and Insert Template in Article. Enterprise's column menu has Add Custom Field; local Odoo has no `web_studio` module. These are Enterprise Spreadsheet/Knowledge/Studio integrations, not missing core Review destinations. The Community database has `spreadsheet` installed but `can_insert_in_spreadsheet` remains false, and Knowledge is uninstallable. Preserve compatibility by treating these as optional integrations; do not make the accounting suite depend on unavailable Enterprise modules. Audit row totals differ (local 5, Enterprise 182) and cannot be compared as the databases contain different records.

## Annual Report default-period parity — 2026-10-29

The live Enterprise annual-report `New` dialog defaulted to January 1 through
December 31 of the previous calendar year, with the current user as a
responsible and the Annual Report template selected. Before this increment, the
local annual-document model used the current company fiscal year (2026 in this
database). Local Annual Report documents now default to the prior full calendar
year. The upgrade installed `accounting_pdf_reports` `2.0.50` and
`om_account_accountant` `20.0.1.34.12`; all five
`TestAnnualReportDocument` tests passed, including date defaults, template
section copying, HTML content and PDF action behavior. Knowledge-backed template
editing remains an Enterprise-only integration; local visual confirmation is
open because the browser session is unauthenticated.

## P&L Cash Basis Method test and database upgrade — 2026-10-29

The Enterprise P&L filter was opened live and showed `Cash Basis Method`; with
the option selected, its toolbar label was `Posted Entries, Cash Basis`. The
local implementation was upgraded on `flousflow_om_accountant_dev20_20261028`
to `accounting_pdf_reports` `2.0.49` and `om_account_accountant` `20.0.1.34.11`.
The focused Odoo transaction test passed (1 test, 0 failures, 0 errors): an
unpaid invoice using an on-payment tax is excluded by Odoo's native
tax-exigible domain; payment creates CABA journal items that pass that domain;
the interactive totals, PDF values and XLSX export preserve the selected basis.
The local `8077` HTTP endpoint returned 200 after restart. Local UI interaction
could not be rechecked because its browser session is unauthenticated, and
matched-data numeric parity and the full P&L hierarchy remain open.

## Inventory Valuation report comparison — 2026-10-30

The live Enterprise Review > Inventory > Inventory Valuation page is
`/odoo/stock-valuation-closing`. It exposes an as-of date and **Generate
Entries**; the observed 2026-10-30 report contains Initial Balance, Stock
Variation, and Ending Stock. The displayed initial balance is zero and the
stock values shown are $735,040.50.

The local Review menu points to the same Odoo core action,
`account.action_report_stock_valuation` (client tag `stock_valuation_report`,
model `account.stock.valuation.report`, path `stock-valuation-closing`). The
core `account` and `stock_account` modules are installed in the 8077 database.
A read-only local ORM calculation for the same date returned the same three
principal report sections; conditional Accruals and Inventory Loss sections
were absent. Local values were zero initial balance, $717,100.50 ending stock,
and balanced $717,100.50 debit/credit detail in Stock Variation. Those amounts
come from different stock and accounting records and do not establish a
calculation gap. The local browser is unauthenticated, so exact row rendering,
date-picker interaction, and **Generate Entries** behavior still need visual
verification after sign-in.

## Deferred schedule default-period parity — 2026-10-30

The live Enterprise Deferred Revenues page is `/odoo/deferred-revenue`. Its
period filter was **September 2026** on 2026-10-30, which is the previous
calendar month. The filter panel exposes period, comparison (previous period,
period count, sort direction, and amount/percentage), journals, grouping, hide
zero/unfold-all options, and currency scale. The settings menu contains XLSX,
Send to Documents, and Insert in Article. The page had no revenue rows.

Local `DeferredScheduleReport` initialized the current month (October 2026)
instead. It now defaults both Deferred Revenues and Deferred Expenses to the
previous calendar month, matching Enterprise. The local ORM returned no
September revenue rows, and two posted expense lines totaling 583.33. This
database also offers a Posted/All Entries selector that was not present in the
inspected Enterprise filter panel; Documents and Knowledge actions remain
Enterprise-only integrations. Enterprise shows only the report title in the
header; local previously added the company name beneath it. The local header now
matches the observed title-only presentation, while XLSX keeps its company
identification. A browser tour checks the rendered header and period behavior.

## Review menu and Journal Audit parity update — 2026-10-30

The authenticated Enterprise Accounting menu showed Review ordered as Control,
Audit, Inventory, Regulatory, Purchases, and Sales. A read-only query of the
local 8077 `ir.ui.menu` records confirmed the same ordered groups and entries.
This verifies installed menu records, not effective visibility for each user's
permission groups.

The live Enterprise Journal Audit showed one **Audit** action per group; it
opened the scoped `account.move.line` list (the Purchases group contained three
documents). Local had a second **Journal Items** button invoking the same
action. That duplicate control was removed while retaining **Audit** and the
distinct **Mark Reviewed** workflow. A pre-upgrade backup is at
`backups/flousflow_om_accountant_dev20-before-journal-audit-parity-20261030.dump`.
The module upgraded to `20.0.1.34.19`; its focused test run passed 4 tests with
0 failures and 0 errors, rebuilt the backend assets, and `/web/login` returned
HTTP 200 after restart. Local visual interaction still awaits an authenticated
browser session.


## Bills To Receive live comparison — 2026-10-30

Enterprise `/odoo/action-843` showed an as-of date of 2026-10-30, vendor
`Gemini Furniture`, and 2 records totaling quantity 25, received 25, billed 0,
average unit price 110.75, and amount 3,095.00. The local ORM returned the
same date-scoped purchase lines for P00005: Office Lamp 20 × 132.50 = 2,650.00
and Office Chair 5 × 89.00 = 445.00. Their aggregate quantity, receipt, billing,
average price, and amount match the Enterprise group. The local list definition
also contains a hidden optional Description column. The Enterprise view's tune
menu exposes **Add Custom Field**, which is an Odoo Studio capability unavailable
in the Community runtime. The local browser session is unauthenticated, so the
rendered local controls remain unverified; Billed Not Received has no local
fixture for a nonempty comparison.


## Sales Review grouped-cost parity — 2026-10-30

The live Enterprise **Invoices To Be Issued** page `/odoo/action-446` showed
Acme Corporation with three S00029 (MANUAL) lines: quantities 15/10/12,
delivered quantities 12/8/10, invoiced quantities 0/0/0, Unit Prices 14,920,
5,222 and 3,730, and detail Total Costs 30,000, 8,000 and 7,000. The grouped row
showed Quantity 37, Delivered 30, Invoiced 0, Unit Price 23,872, Amount 258,116,
and Unit Cost 4,200; it did not show a grouped Total Cost subtotal. The live
**Invoiced Not Delivered** page `/odoo/action-447` had no rows.

Local read-only ORM checks on 8077 at the same as-of date found no lines in
these sales queues, so financial values cannot be compared. The local view had
requested `sum` on Total Cost in both sales queue list views, unlike Enterprise.
I removed only those two view aggregators; line-level Total Cost and its
calculation remain, and Unit Cost still aggregates. Before the update, a 14 MB
backup was saved at
`backups/flousflow_om_accountant_dev20-before-sales-review-cost-total-20261030.dump`.
`om_account_accountant` upgraded to `20.0.1.34.20`; the focused
`TestReviewAccrualCosts` run passed 9 tests with 0 failures and 0 errors, and
`/web/login` returned HTTP 200 after restart. Local visual confirmation still
requires an authenticated browser session.
