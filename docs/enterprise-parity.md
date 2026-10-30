# Odoo Enterprise Accounting Parity

Scope: compare the FlousFlow Odoo 20 Community accounting database and module with the connected Enterprise accounting database. This is a living gap register, not a claim of full parity.

Last reviewed: 2026-10-30

## Customer Statement formula tooltip parity — 2026-10-30

The live Enterprise Customer Statement was inspected on fiscal year 2026 with
populated partner balances. Its total information popover identifies the engine
as “Custom Python Function,” shows `_report_engine_partner_ledger_report` as
the Formula, and lists the sub-formulas `_currency_amount_currency`, `amount`,
`amount_currency`, `date_maturity`, and `invoice_date`. The local tooltip
previously omitted the Formula and `_currency_amount_currency` sub-formula, and
showed a locally derived expression for `invoice_date`. The local Customer
Statement now uses the observed Engine, Formula, Sub Formula and Value fields in
both report and total info popovers, with Arabic translations matching the live
labels. `accounting_pdf_reports` `2.0.54` is installed on the local 8077
database; the module upgrade completed and `/web/login` returns HTTP 200. Local
visual tooltip verification remains open because the browser session is logged
out.

## Customer Statement company-currency column parity — 2026-10-30

The populated Enterprise fiscal-year statement showed Ready Mat's USD journal
line in the Amount column and left Amount in Currency blank. The local statement
formatter previously printed `amount_currency` for every line, which repeats a
company-currency amount in that column. It now leaves the cell blank when the
line currency is the company's currency and continues to format lines in a
different currency. The current local database has 25 posted receivable lines,
but foreign-currency output still cannot be compared without a line whose
currency differs from the company currency.

## Customer Statement account-scope labels — 2026-10-30

The live Enterprise account-scope menu exposes Trade Receivable, Non-trade
Receivable, Trade Payable, and Non-trade Payable. Its default combined label is
Trade Partners. The local report already had the same four scopes and backend
account-type domains, but the option labels were embedded as plain text and had
no Arabic translations. The options now use Odoo's translation function, and
the Arabic labels match the live menu. The combined Trade Partners label also
has its Arabic translation. Local visual confirmation remains open while the
8077 browser session is signed out.

## Verified comparison

| Requirement | Enterprise support | Local evidence | Actual gap | Next step |
| --- | --- | --- | --- | --- |
| Accounting application icon | The live Enterprise Accounting app tile uses a 100×100 multicolor accounting icon. | The module icon now matches the live Enterprise tile byte for byte (SHA-256 `e6f62706fb9ba8d6250d1391ac745c2a8c3cc2ab61dbf9db9a2db0f16a5e8e15`). `account.menu_finance` points to it, and the local menu's stored icon attachment checksum matches the updated file after installing `om_account_accountant` `20.0.1.34.16`. | The local Community app launcher does not render the same tile grid, so icon appearance there could not be directly compared in-browser. | Keep the Enterprise-sourced icon on the Accounting menu and verify future changes against the live tile asset. |
| Review menu destinations | Live Enterprise Review has Control (Journal Items, Audit Trail, Journal Audit), Audit (Working Files, Annual Report), Inventory (Inventory Valuation), Regulatory (Unrealized Currencies, Deferred Revenues, Deferred Expenses), Purchases (Bills To Receive, Billed Not Received), and Sales (Invoices To Be Issued, Invoiced Not Delivered). | A recursive query of the current 8077 clone's active menu tree returned the same ordered groups and children, including native Audit Trail and the custom Journal Audit. | Menu records and labels match; equal workflow behavior and effective permissions for every user are not established by this comparison. | Continue checking each destination's view, data and permissions, starting with Journal Audit and accrual queues. |
| Reconciliation workflow | Enterprise `/odoo/reconcile` defaults to posted lines with residuals, grouped by Account then Partner. It shows Date, Journal Entry, Description, Currency, Debit, Credit, Matching and Remaining, with an **Auto Reconcile** button per group. | Local `Accounting > Reconciliation > Match Journal Items` lists posted, unreconciled entries on reconcilable accounts and groups by Account and Partner; users select lines and open a manual Match wizard. Local Bank Reconciliation and Open Items remain available separately. A duplicate Reconciliation folder and three duplicate shortcuts were deactivated; the unique Transactions to Review entry is under the original Accounting > Reconciliation folder. The focused menu suite passed all 6 tests after upgrade to `20.0.1.34.35`. | Local still lacks the Enterprise residual-group review screen and per-group Auto Reconcile action. No reconciliation was triggered in Enterprise, and database balances are not comparable. | Design and verify safe per-group matching on isolated fixtures, including partial matches, ambiguous candidates and multi-currency cases. |
| Inventory Valuation | Enterprise `/odoo/stock-valuation-closing` has an as-of date, **Generate Entries**, and Initial Balance, Stock Variation, and Ending Stock sections. On 2026-10-30 it showed zero initial balance and $735,040.50 in the displayed stock values. | Local menu points to the same core action `account.action_report_stock_valuation` (`stock_valuation_report`, `account.stock.valuation.report`, `stock-valuation-closing`). A read-only ORM calculation for 2026-10-30 returned the same three principal sections; Accruals and Inventory Loss were absent. Local values were zero initial balance, $717,100.50 ending stock, and balanced $717,100.50 debit/credit details in Stock Variation. | Local browser session is unauthenticated, so exact rendered rows and Generate Entries interaction are not visually verified. The two databases have different stock/accounting records, so their amounts are not a valid direct parity comparison. | Sign in locally to compare row expansion, date picker, and Generate Entries; compare amounts only on aligned stock moves, accounting entries, company and date. |
| Deferred Revenues / Deferred Expenses | The live Enterprise Deferred Revenues report at `/odoo/deferred-revenue` defaults to September 2026 and shows only the report title in its header. Its filters include search, period, comparison, journals, account/category/product grouping, options (Unfold All and Hide lines at 0), and currency scaling. Print is available; settings expose XLSX, Documents and Knowledge/article actions. | Local `om_account_accountant` `20.0.1.34.23` defaults both reports to the previous calendar month. The browser report header now omits the company label to match Enterprise, while XLSX retains company identification. A focused browser tour checks the header and period behavior. | The local report retains a Posted/All Entries filter absent from Enterprise's inspected filter panel; Documents and Knowledge actions are unavailable in Community. The local UI remains unauthenticated, so only the automated browser tour verifies its rendering. | Compare both reports on matched asset schedules; verify the local header and controls in the interactive browser after sign-in. |
| Audit Trail review workflow | Enterprise `/odoo/action-325` currently exposes Date, Author, Name and Description; search filters are Journal Entry, Account, Taxes, Partners, Company, Restricted and Date; grouping is Date and Updated Data. Its actions menu shows Export and Knowledge options (Insert View in Article, Insert Template in Article); the view settings include Add Custom Field. | Local 8077 database has the same Odoo 20 core `mail.message` action, list view and search view installed. The local core XML defines matching record-type filters, Restricted/Date filters and Date/Updated Data groupings. | Local visual comparison is still pending sign-in. The current Enterprise view did not show a Spreadsheet action despite earlier notes; availability needs a fresh permission/app check. | Compare the local filter/group controls when signed in; verify whether Spreadsheet actions are enabled for the target account before treating them as required parity. |
| Working File review checklist | Enterprise Working Files shows sectioned review cards with inline notes, four checklist states, evidence upload, reviewer activity, and a separate Reviewed/Certify stage. The live 2025 file has 52 checks, 18 resolved and 34 pending; a read-only DOM check confirms Certify is enabled and the pending-check menu exposes the four expected states. Its detail page exposes Cycles, Balances and Spreadsheet tabs. | Local `om_account_accountant` `20.0.1.34.28` implements the four states, notes, evidence attachments and matching tabs. Mark Reviewed permits unresolved checks; certification rejects pending checks. Existing direct Validate from In Progress remains for backward compatibility. Non-managers cannot set Supervised via either create or write. The full `TestWorkingFileBalances` class passed 12 tests on local 8077. | An enabled Enterprise button does not establish that the server accepts certification with pending checks. No click was made on the live audit. Local stage layout, note autosave and evidence upload/removal are not visually verified because the session expired. | Compare certification behavior on a disposable Enterprise record; after local sign-in, verify the Reviewed/Certify controls, note persistence and evidence upload/removal. |
| Bills To Receive accrual queue | Enterprise at `/odoo/action-843` shows an as-of date, last-365-days scope, vendor grouping, purchase/order columns, and an **Add Custom Field** action. On 2026-10-30 Gemini Furniture showed 2 records, quantity 25, received 25, billed 0, average unit price 110.75 and amount 3,095.00. | Local `review_menu.xml` defines the matching columns, vendor grouping and 365-day scope; `review_accrual_list` adds the as-of date. A local ORM read returned P00005 lines 20×132.50 and 5×89.00, matching Enterprise quantities and aggregate amount exactly. `Billed Not Received` is empty locally. A hidden optional Description column is local-only. | Local browser rendering is unverified. Enterprise **Add Custom Field** is an Odoo Studio capability unavailable in this Community runtime; a nonempty Billed Not Received example is still needed. | Compare the local screen after sign-in and add an equivalent billed-but-not-received fixture for numeric comparison. |
| Sales accrual review queues | Enterprise Review > Sales has **Invoices To Be Issued** and **Invoiced Not Delivered**. On live `/odoo/action-446` at 2026-10-30, Acme showed 3 lines and a grouped Unit Cost of 4,200, but no grouped Total Cost subtotal; detail Total Cost values were 30,000, 8,000 and 7,000. Invoiced Not Delivered was empty. | Local has the same columns and computes line-level costs. I removed the group `sum` from Total Cost in both sales lists, retaining Unit Cost grouping and per-line Total Cost. The local ORM has no matching sales rows at that date. Version `om_account_accountant` 20.0.1.34.23 is installed on 8077. | Local visual rendering and matched numeric comparisons remain unverified because the browser session is unauthenticated and both local sales queues are empty. | Sign in locally and verify group and line values against matching sales data. |
| Financial formula details | Balance Sheet rows expose Engine, Label, Formula and Value; Current Assets uses `BA.balance + REC.balance + CAS.balance + PRE.balance`, and tooltip amounts stay unscaled at `k$`. Enterprise P&L shows nine summary rows; its formula details include Revenue `income/-sum`, Gross Profit `REV.balance - COS.balance`, Operating Income `REV.balance - COS.balance - EXP.balance`, and Net Income `REV.balance + OIN.balance - COS.balance - EXP.balance - OEXP.balance`. | Local `accounting_pdf_reports` `2.0.73` now renders the same nine flat P&L rows, with formula metadata on every row and account/journal-item drill-down on the domain categories and totals. Focused tests verify the layout, formulas, and nonzero values for revenue, direct costs, operating expense, other income, depreciation, and other expenses. | The live Enterprise data cannot be numerically equated with the local database; its P&L was empty while the local demo records are populated. Nonzero `k$` tooltip, multiple comparison periods, and financial-budget amounts remain unverified in a signed-in local browser. | Compare matching entry fixtures, then inspect the P&L at `k$` and with comparison/budget columns enabled. |
| Profit and Loss Cash Basis Method | Enterprise's live filter exposes Cash Basis Method; when selected, the toolbar reads “Posted Entries, Cash Basis”. | Local report totals and drill-down use Odoo's native tax-exigible domain; the choice is carried into PDF and XLSX. A payment-based-tax transaction test verifies unpaid exclusion, the generated cash-basis entry passing the native filter after payment, and consistent report/PDF/XLSX results. Installed versions are `accounting_pdf_reports` `2.0.50` and `om_account_accountant` `20.0.1.34.12`; the focused test passed. | The local browser is unauthenticated, so checkbox interaction and toolbar rendering remain visually unverified. Full hierarchy and matched-data numeric parity remain open. | Verify the local control after sign-in and compare the report on equivalent accounting fixtures. |
| Annual Report | Enterprise showed a setup Kanban; New opens a dialog with title placeholder `Example, Annual Financial Overview FY`, prior calendar year dates (2025), current user and Annual Report template. | Local ORM defaults match the prior full calendar year, active user and template. `accounting_pdf_reports` `2.0.71` matches the Enterprise title placeholder in English and its Arabic PO translation; six focused annual-document tests pass and the version is installed on 8077. | Local browser is unauthenticated; the dialog layout and Arabic translation are not visually verified, and Arabic is not enabled in this database. Knowledge article editing remains an unavailable Community integration. | Sign in locally to compare the New flow, content editing and PDF; enable Arabic before comparing translated UI. |
| Report action menu | On the Enterprise Balance Sheet, the settings menu showed XLSX, Send to Documents, and Insert in Article. | The local Balance Sheet report action menu showed XLSX only. The local runtime has no `documents` addon in the Odoo 20 addons tree; `knowledge` is marked uninstallable. | Send to Documents and Insert in Article are missing and depend on Enterprise apps that are not available in this Community runtime. Adding UI-only placeholders would not provide the workflows. | Keep these as Enterprise-only gaps until the corresponding supported apps/APIs are available or an approved Community alternative is chosen. |
| Customer / Vendor Statement | Enterprise has a full-page Customer Statement at `/odoo/customer-statement`, with month/quarter/fiscal-year/custom periods, trade and non-trade receivable/payable scopes, partner/tag filters, posted/all-entry filters, currency scaling, document/date/due-date/amount/amount-in-currency columns, expandable partner balances, Partner and Journal Items actions, a per-line `⋮` menu, formula info popovers, Print/Send, and XLSX in report settings. The live page opened on September 2026 (the previous month); its More menu contains Send. | Local now defaults to the previous calendar month in the interactive view, API, and XLSX route; it has the same report controls, data columns and drill-downs. In the local 8077 browser, Send is now inside a More dropdown like Enterprise, while XLSX remains in Report options. `accounting_pdf_reports` is now installed at `2.0.70`; the earlier runtime rendered the More > Send action. | Enterprise Send to Documents and Insert in Article require apps absent from this Community runtime. The XLSX export still needs populated-data verification; local and Enterprise databases have different statement rows and totals. More than 10,000 lines are rejected rather than paged. | Compare XLSX values on matched fixtures; verify Print/PDF and the email composer. |
| Partner Ledger / customer or vendor statement | Enterprise opens `/odoo/accounting/partner-ledger` with Journal, Account, Date, Due Date, Matching, Debit, Credit, Amount Currency and Balance, expandable partner rows and Partner/Journal Items actions. Filters include fiscal year, account scope, partners/tags, posted/all entries and currency scale; settings expose XLSX. It also warns about unposted entries in or before the period. | Local path: Accounting → Reporting → Partner Ledger → Print → Document Type → Balance Confirmation; the same print wizard is available from an individual partner's Print menu. The selector offers Account Statement and Balance Confirmation. The confirmation PDF was generated for Acme Corporation from 8 posted receivable lines through 2026-12-31; closing balance 53,151.99 with agree/disagree options. The Journal Items row action preserves the report's Posted Entries / All Entries choice. Database inspection confirms demo-like accounting records are present (45 partners, 64 posted moves). A new isolated test verifies the confirmation balance includes pre-period movements through the selected end date; all 4 Partner Ledger tests passed. A single selected customer/vendor now resolves the matching receivable/payable side automatically when the interactive report's default scope is both sides. | The local wizard was displayed with Balance Confirmation selected, but the print action encountered an expired Odoo session, so PDF generation and visual layout were not reverified this turn. XLSX values and warning/menu placement remain unverified against matched data. | Reopen a local session and review the confirmation PDF; verify Journal Items with both move-state choices, then compare non-empty report/XLSX output and warning behavior on equivalent data. For partners with both or neither role, select Receivable or Payable explicitly before printing the confirmation. |
| Aged Receivable / Aged Payable | Enterprise report rows expose Partner and Open Items actions beside each partner, plus as-of date, account/date basis/period/move-state filters, currency scale, aging buckets, expandable balances and move drill-down. | Local supports the report filters, bucket calculation, scale and drill-down; partner rows include Partner and Open Items actions. Open Items now opens the interactive report described below instead of a generic journal-item list. | Local and Enterprise use different accounting data, so aged totals are not directly comparable. | Compare rows and action results on matching posted, reconciled and foreign-currency fixtures. |
| P&L selected-budget parity | Enterprise P&L exposes a searchable Budget selector with a Create action. | `accounting_pdf_reports` 2.0.23 now provides a searchable dropdown, filters existing budgets as the user types, allows clearing the selection, and opens the existing create-budget dialog prefilled from the search text. Existing budget selection still reloads the report. Backend calculation/export tests passed on an isolated database; module upgrade also succeeded on the primary local development database. | The local browser session is still unauthenticated, so visual behavior and keyboard/dropdown interaction have not yet been confirmed in the running UI. Enterprise budget creation semantics and date-range allocation have not been fully compared. | Re-authenticate the local browser session; compare the selector interaction, create flow, date-range allocation, and printed/exported values against Enterprise before calling this area matched. |
| Dashboard KPI actions and ordering | On the live Enterprise account inspected 2026-10-30, the visible financial KPI cards are Customer Invoices, Expenses, Receivable, and Payable, plus Setup Your Invoice Layout. Their destinations are `/odoo/accounting/customer-invoices-analysis`, `/odoo/accounting/profit-and-loss`, `/odoo/accounting/aged-receivable`, and `/odoo/accounting/aged-payable`. | The local 8077 cards open equivalent destinations: Customer Invoices → `/odoo/accounting/customer-invoices-analysis`, Expenses → P&L `/odoo/accounting/action-450`, Receivable → Aged Receivable `/odoo/accounting/action-656`, Payable → Aged Payable `/odoo/accounting/action-657`. The local Cash card opens native `/odoo/accounting/cashflow-analysis`. Dragging Cash to the front persisted after a page reload; the original per-user order (`invoices`, `cash`, `payable`, `expenses`, `receivable`, `invoice_layout`) was restored and confirmed in PostgreSQL. | This Enterprise user's dashboard has no separate Cash KPI, while local Community displays one. Keep it as a local-only extra capability unless the user requests strict card-set parity. Card amounts and saved order are account-specific and differ between databases; phone/tablet drag behavior has not been verified. | Preserve current saved order and verify responsive reordering at tablet/phone widths; compare again if the Enterprise account's configured KPI set changes. |
| Partner Open Items smart button and report | Enterprise partner More menu opens an interactive report with as-of date, Trade Partners/Receivable/Payable, Posted/All Entries, partner search, currency scale, No Reminder, invoice/due dates, amount/currency/residual columns, Partner and Journal Items actions, Print, Send and XLSX. Ready Mat showed -$6,936.00. | The local partner button opens a responsive report using Odoo's native residual-at-date fields. It includes matching filters and columns, writes No Reminder through the native inverse, shows the unposted-entry warning, reuses the existing follow-up reminder wizard, prints QWeb PDF and exports RTL XLSX. Ready Mat currently returns 4 payable lines totaling -$9,727.62 and 1 unposted journal item. Backend/PDF/XLSX tests and a Chrome report tour passed. Installed versions: `accounting_pdf_reports` `2.0.74`, `om_account_accountant` `20.0.1.34.33`. | Local and Enterprise totals differ because their accounting entries differ. The user's local browser session expired during service restart, so visual verification in the user's session and the reminder composer still need a check. Send to Documents and Insert in Article depend on Enterprise apps unavailable in this Community runtime. | Sign in and inspect the Ready Mat report; compare equivalent entries, open the reminder composer without sending, and keep Documents/Knowledge actions documented as Community gaps. |
| Cash Flow Statement | Live Enterprise `/odoo/cash-flow` shows month/quarter/fiscal-year/custom periods, posted/draft/all plus hide-zero, scale, expandable detail, source-line drill-down, Print and XLSX; Documents and Knowledge actions are present. The table omits company/Description headings and labels investing as “Investing and Extraordinary Activities.” | Local `accounting_pdf_reports` `20.0.2.0.79` retains the matching report controls and headings/section label. For September 2026, Enterprise displayed zero opening, net and closing balances. The same period in local 8077 returns opening 0, net change 2,425 and closing 2,425. Three posted local bank lines (2,000, -850, +1,275) post against suspense account 101402 and remain unreconciled. | The amount difference is explained by local records absent from Enterprise's report for this period; matched-data parity remains unproven, and no calculation defect is established. Local keeps an optional journal filter. Documents/Knowledge actions are unavailable in Community. Local visual verification requires sign-in. | Compare matching cash movements and reconciliation state; verify local interactive/PDF/XLSX output after sign-in. |
| Journal Audit | Enterprise at `/odoo/journal-report` filters by period, posted/draft/all entries, payments and scale; the 2026-10-30 Purchases group had 3 documents and 0 To Review. Groups expand into account totals and Applied Taxes, followed by a global Tax Summary. Its single **Audit** action opens the scoped Journal Items list grouped by Journal Entry. Settings expose XLSX, Send to Documents and Insert in Article. | Local has the same filters/details. **Audit** opens the scoped `account.move.line` list and enables the same Journal Entry grouping. Toolbar now matches Enterprise: Print and Report options in the action row; period, target moves, Include Payments and scale shown by default on desktop. The filter toggle is limited to phone widths. The company label was removed and Odoo-native icons are used. Version `20.0.1.34.34` is installed on 8077; desktop and 390×844 Chrome tours passed, including period selection and phone filter collapse/expand. | Matched-data amounts and Enterprise phone/tablet rendering remain unverified. Documents and Knowledge actions are unavailable in this Community runtime. | Compare amounts on equivalent records and inspect Enterprise's responsive toolbar at phone and tablet widths. |

## Evidence boundaries

- Enterprise evidence came from the connected `edu-flousflow.odoo.com` browser tab on 2026-10-29.
- Local UI evidence came from the running `http://127.0.0.1:8077` session and is scoped to the stated UI observations; the browser session later expired after an Odoo restart. The local Odoo database is `flousflow_om_accountant_dev20_20261028`.
- Report balances differ between databases and are not treated as a parity defect without matched accounting data, company, date, and report filters.
- The Review menu comparison does not establish ACL or record-rule parity.

## Current implementation state

- Local branch: `20.0`.
- `om_account_accountant`: installed, `20.0.1.34.35` on `flousflow_om_accountant_dev20_20261028`. Its Accounting menu icon attachment matches the live Enterprise tile image byte for byte. The installed Review menu records match the observed Enterprise order; Journal Audit opens lines grouped by entry. The filter row is visible by default on desktop and collapsible on phone widths. Focused Chrome tours passed at desktop and 390×844, including period selection and the phone filter toggle; Enterprise phone/tablet layout has not yet been observed. Accounting > Reconciliation now has one active folder; duplicate shortcuts were deactivated and the unique Transactions to Review entry moved under the existing folder. All 6 focused menu tests passed. The Enterprise residual-group reconciliation screen still has no direct local equivalent. Sales Review totals match Enterprise grouping (Unit Cost subtotal, line-level Total Cost without a group subtotal). Deferred Revenues and Expenses default to the previous calendar month and omit the extra company label from the report header. Working File supervised-state server authorization is manager-only. Current Enterprise `Audit 2025` renders seven upload actions; version `20.0.1.34.33` restores the corresponding seven local template/check flags, including two legacy checks without `template_id`. A fresh local visual check, note persistence, and actual evidence upload/removal remain unverified.
- `accounting_pdf_reports`: installed, `20.0.2.0.79` on the current 8077 test clone (Customer Statement defaults to the previous month observed in Enterprise, its formula tooltip uses the observed engine/sub-formula metadata, company-currency amounts are omitted from Amount in Currency, account-scope labels are translated to match Enterprise, and Send is under More; Balance Sheet tours verify Current Assets/Total ASSETS formula popovers and XLSX return flow; P&L has Enterprise's nine-row summary with formula popovers and drill-downs; matched-data values, nonzero `k$`, comparison and budget columns remain open; Partner Ledger has single-partner balance-confirmation output with a cumulative closing balance, posted entries, one receivable/payable side, and unsigned agree/disagree response; Journal Items preserves Posted Entries / All Entries; Partner Ledger filters collapse behind a translated phone-width toggle; P&L Cash Basis Method passes through interactive, print and XLSX; Annual Report documents default to prior year; Cash Flow PDF follows interactive order and suppresses a zero net-change amount; Tax Report provides both Enterprise grouping layouts, period comparisons, XLSX export and journal-item drill-down; 14 focused post-tests passed, with withholding skipped because its localization is absent; depends on Odoo's wkhtmltopdf report-engine addon. Local browser visual checks still require sign-in.)
- Responsive report pass: Partner Ledger, Customer Statement, General Ledger, Trial Balance, and Financial Report toolbars now wrap at tablet widths; wide tables scroll inside their report panels; phone-width controls/popovers are constrained to the viewport. Partner Ledger now collapses report filters behind a toggle at widths up to 767px, matching the Enterprise narrow-screen affordance. On 2026-10-30 the module upgraded to `2.0.70`; the CSS bundle compiled without Sass errors and Odoo served HTTP 200. The local session is unauthenticated, so this latest responsive layout and phone/tablet widths still need direct visual verification.
- Remaining differences are tracked above; parity is incomplete.

## Partner Ledger live comparison — 2026-10-30

A fresh read-only inspection of the authenticated Enterprise report at
`/odoo/accounting/partner-ledger` confirmed its expanded filters are Search,
fiscal year, Trade Partners account scope, Partners, Posted Entries and currency
scale. The table includes Journal, Account, Date, Due Date, Matching, Debit,
Credit, Amount Currency and Balance; partner rows expose Partner and Journal
Items actions. The report shows the unposted-entry warning and a top-level Print
button. At the time of inspection the Enterprise data showed Gemini Furniture
at $3,095.50 and Ready Mat at $6,936.00. These figures are not a matched-data
comparison with the separate local demo database.

The report settings menu exposes XLSX, Send to Documents and Insert in Article.
Only XLSX is available in the inspected Community runtime because Documents is
not installed and Knowledge is unavailable there.

The local Partner Ledger source provides the same report controls, columns,
row actions and warning. Its Balance Confirmation document type is an explicit
FlousFlow addition: the inspected Enterprise report exposes Print but no
confirmation document-type choice. On 2026-10-30, the local database has
`accounting_pdf_reports` `20.0.2.0.79` and `om_account_accountant`
`20.0.1.34.33` installed. The wizard is reachable from Accounting → Reporting
→ Partner Ledger → Print; its Document Type selector offers Account Statement
and Balance Confirmation. A local run generated and visually inspected the
Acme confirmation as a one-page A4 PDF, with the cumulative closing balance
53,151.99 as of 2026-12-31, agree/disagree choices, and no signature field.
The database contains Odoo accounting demo data: Acme Corporation and Ready Mat
are present, and the account demo invoice external IDs resolve to 11 posted
moves. A fresh read-only check on 2026-10-30 confirmed that local client action
655 is Partner Ledger, the installed wizard view contains the Document Type
selector, and Acme Corporation (partner 831) has eight posted moves. The local
8077 service responds with HTTP 200.

After the latest service restart, a fresh print through the local browser has
not been verified because the local browser session needs sign-in. The 8077
login page returns HTTP 200;
`report.pdf_engine_default` is `wkhtmltopdf`, and the installed binary reports
version 0.12.6 with patched Qt. These checks establish that the report option
and PDF engine are present, while a fresh print through the current browser
session still needs sign-in.


## Partner Ledger detail-row parity — 2026-10-30

The expanded live Enterprise Partner Ledger rows show the move label (for
example `فاتورة/2026/10/0001`), journal name, account code, dates, and a per-line
More menu whose action is **View Journal Entry**. Before this pass, local rows
showed journal codes (`INV`/`MISC`) and combined account display names; the
date link also passed an `account.move.line` ID into an `account.move` action.
The local API now returns move label, journal name, account code and move ID;
the detail row has the Enterprise action menu, and both the label and date open
the correct move.

`TestPartnerLedger` now checks these detail fields. `accounting_pdf_reports`
`20.0.2.0.68` was upgraded on local 8077 after a 14 MB database backup at
`backups/flousflow_om_accountant_dev20-before-partner-ledger-row-action-20261030.dump`;
the focused run passed 3 tests (0 failures, 0 errors). The local Partner Ledger
API now returns Acme's 8 entries with journal names and account codes, the
rebuilt backend bundle includes the row-menu handler, and `/web/login` returns
HTTP 200. The local authenticated UI still needs a visual check.

The Odoo Arabic catalog now translates the row-menu accessibility label and
**View Journal Entry** action. `msgfmt --check` succeeds (the catalog reports
its pre-existing missing `PO-Revision-Date` header); `accounting_pdf_reports`
`20.0.2.0.70` is installed on 8077, and the rebuilt backend JS bundle contains
the row-menu handler and template. The focused Partner Ledger class passed again
with 3 tests, 0 failures and 0 errors.

The local database currently has only `en_US` active. The new Arabic menu strings are present in `i18n/ar.po` and the catalog parses, but Arabic rendering is not verified or active in this database.

The final Partner Ledger row layout now renders the journal name beneath the move
label in the Journal cell, matching the expanded Enterprise row hierarchy. The
latest `2.0.70` upgrade passed the same 3 focused tests, and Odoo served the
rebuilt template through the backend bundle with HTTP 200. A separate 14 MB
backup was taken immediately before this final upgrade at
`backups/flousflow_om_accountant_dev20-before-partner-ledger-journal-label-20261030.dump`.

## Tax Report interactive screen — 2026-10-30

The live Enterprise Tax Report is a full-page interactive report. Its toolbar
shows period, Comparison, Posted Entries, the General Tax Report selector and
currency scaling; the page shows an unposted-entry warning, a Net/Tax table,
Print and report actions for XLSX, Documents and Knowledge.

The working tree now routes the existing Tax Report menu to a new OWL screen.
It exposes date range, Posted Entries / All Entries and four currency scales,
shows Sales, Purchases and Withholding rows with subtotals, and warns when
draft entries affect the selected period. The new ORM method calls the same
`get_lines` aggregation used by the existing PDF report; its Print button opens
the existing wizard, retaining localized tax-grid printing and Close Tax
Period.

Static Python compilation, JavaScript syntax, XML parsing and `git diff
--check` passed. A read-only Odoo shell run against the actual 8077 database
compared the interactive result with the PDF engine and found identical rows
for FY2026: Sales net 47,574.00 / tax 6,262.50; Purchases net 10,031.00 / tax
1,040.40; 8 draft entries. A rolled-back invoice fixture then verified Posted
Entries excludes a draft's 500.00 base, All Entries includes it, and the
unposted warning increases by one without leaving test records behind.

An isolated PostgreSQL 17 clone upgraded to `accounting_pdf_reports`
`20.0.2.0.75`. The installed Tax Report menu points to client action
`accounting_pdf_reports.tax_report`. `TestTaxReport` passed with 6 post-tests,
0 failures and 0 errors; the withholding test was skipped because its
localization is not installed. The clone and temporary Odoo process were
removed after verification.

A later comparison pass added the Enterprise comparison modes to the working
screen and export: previous periods (up to 12), same period last year, custom
dates, and ascending/descending ordering. Each selected period supplies its
own Net/Tax columns; XLSX uses the same periods and totals. `TestTaxReport`
passed on the host-backed PostgreSQL 17 clone: 10 post-install tests, 0 failures
and 0 errors; withholding was skipped because its localization is not installed.
The clone is still available as container `ff-tax-report-test-pg` on port 55440,
with database `postgres`, and now runs `accounting_pdf_reports` `20.0.2.0.78`.
A Chrome headless tour on that clone rendered the full-page report, selected
Previous Period and confirmed that setting the period count to 2 shows three
period columns. The actual 8077 browser session is still unauthenticated, so
this is clone rendering evidence rather than a user-session visual check.

The local 8077 service now connects to a host-backed PostgreSQL 17 clone on port
55440 and reports `accounting_pdf_reports` `20.0.2.0.79`. The original database
on PostgreSQL port 55439 remains intact at `20.0.2.0.74`. The cloned database
upgrade and focused test run completed: 14 post-tests, 0 failures, 0 errors;
the withholding case was skipped because its localization is absent. A Chrome
headless tour rendered the report and selected both grouping modes. The user's
local browser session is logged out, so personal-session visual verification
and an authenticated XLSX HTTP download remain unverified. XLSX workbook
contents are covered by tests. PDF output does not yet support all comparison
columns. Documents and Knowledge actions require Enterprise apps absent from
this Community setup.
