# Review Menu and Report Parity

Last live comparison: 2026-10-28

This ledger tracks the Community implementation against the FlousFlow Enterprise
Odoo 20 database. Menu names and report options are observations from the live
Review menu and report screens. Financial totals must be compared only on matched
company data and period.

The local Review menu follows the live grouping and order: Control (Journal
Items, Audit Trail, Journal Audit, then the suite-specific Entries to Review
queue), Audit (Working Files, Annual Report),
Inventory, Regulatory (Unrealized Currencies, Deferred Revenues, Deferred
Expenses), Purchases, then Sales. `Draft Entries` remains an additional
community work queue under Accounting.

## Journal Audit

| Capability | Enterprise | Community | Status |
| --- | --- | --- | --- |
| Review menu hierarchy | Control: Journal Items, Audit Trail, Journal Audit | Same order, then suite-specific Entries to Review; Draft Entries remains under Accounting | Implemented and verified by Odoo menu tests |
| Review menu entry and interactive report | Yes | Yes | Implemented |
| Period, posted/draft/all entries | Month, Quarter, Fiscal Year and custom dates; posted, draft, or all | Month, Quarter, Fiscal Year and custom dates; posted, draft, or all | Browser tour verified period selection, quarter navigation, and custom date entry |
| Include payments | Yes | Yes | Implemented |
| Display scale | Currency, thousands, millions | Currency, thousands, millions | Implemented |
| Journal totals and expandable entries | Yes | Yes | Implemented |
| Review action | Marks entries reviewed; the per-journal action remains visible at zero pending | Calls Odoo's native `set_moves_checked` for eligible posted entries; the action is visible at zero pending and returns 0 without writes | Browser verified on the local zero-pending journal; handler remains company, period, state and group scoped |
| Tax summary and drill-down | Tax Summary links to the Taxes Applied journal-item list, grouped by Taxes then Account | Same destination and grouping; company, report period, target move state, and payment inclusion follow Journal Audit | Browser tour verified the destination and both active groupings; tax rows can also be opened individually |
| Print | Yes | Yes | Implemented |
| XLSX export | Yes | Yes; Journals, Entries, and Taxes worksheets | Implemented and downloaded/validated |
| Send to Documents | Yes | No Documents module in the local addon path/database | Remaining platform integration |
| Insert in Article | Yes | No equivalent Knowledge integration in the local addon path/database | Remaining platform integration |

The live Enterprise report showed three entries awaiting review and a nonzero
Purchases balance. The local development database showed one posted
Miscellaneous Operations entry with no review pending and zero balance. These
are different databases and are not evidence of a report-calculation mismatch.

The local Review menu exposes the native Journal Items action at the same
position as Enterprise. Its pre-existing Entries to Review action remains as
an additional destination after the three Enterprise entries; the journal-item
action also remains available under Accounting > Transactions.

## Balance Sheet and Profit and Loss

Enterprise shows an information icon for each report line. Its popover exposes
the engine, label, formula, and calculated value. The Community Balance Sheet
now returns this formula metadata for every line and renders the icon for
regular users as well as developers. A read-only call against the local 8077
database returned 28 report lines with formula metadata; `Total ASSETS` reports
`CA.balance + FA.balance + PNCA.balance`. A headless browser tour on the local
database confirmed an info icon on every displayed row, then opened Total
ASSETS and verified that the popover shows Engine, Label, Formula, and Value,
including the expected aggregate formula. Numeric parity still requires
matching company data and report dates.

## Deferred Expenses and Deferred Revenues

The live Deferred Expenses report has month, quarter, fiscal-year, and custom
date-range selections; no comparison or a selected number of previous periods;
ascending or descending ordering; comparison by amount or percentage; grouping
by account, product category, or product; options to show all entries and hide
zero lines; currency scale; print; and XLSX, Documents, and article actions.
The live screen currently has no rows. Deferred Revenues is also available under
Review.

The local suite has `om_account_asset` asset and revenue-recognition boards.
Review now exposes separate Deferred Expenses and Deferred Revenues interactive
reports. They use the monthly asset schedule moves and their actual recognition
account lines, with month/quarter/fiscal-year/custom date selection,
posted/all entries, account/category/product grouping, the journal selector,
a selected count of preceding-period comparisons, amount or percentage changes,
ascending/descending ordering, hide-zero, company-currency scaling, print, and
drill-down to the matching journal entries. Their XLSX export includes Schedule
and Entries worksheets and preserves period and comparison filters. New assets
retain their source invoice line so product grouping can use the actual product.

Remaining differences: the Enterprise actions to send the report to Documents
or insert it into an article are unavailable because those apps are absent from
the local Odoo 20 addons path. Existing assets created before the
source-invoice-line field was added have no product link and fall back to the
asset name for product grouping. At the time of comparison, the local database
had zero assets, asset categories, asset schedule moves, and invoice lines
assigned to asset categories. The live Enterprise report also had no rows, so
nonzero schedule arithmetic has not yet been validated against matched records.
An isolated accounting fixture now verifies nonzero quarter totals and prior-
period comparison against three posted depreciation moves (300.00 each total),
and confirms that a February drill-down returns only the February move. A live
matched-company comparison remains outstanding.

## Working Files

Enterprise exposes Working Files from Review as an audit dossier, not as a
Documents folder. The current live cycle screen exposes Cycle and Balances
navigation. Its audit checklist contains 52 checks grouped by accounting area,
with review states, notes, evidence uploads, and activity history. The cycle also
has a Spreadsheet tab. The observed Enterprise file opens a blank Sheet1 in the
spreadsheet editor, with File/Edit/View/Insert/Format/Data/Help menus and a
"Saved" status indicator. Editing and persistence across reloads have not yet
been exercised.

The Community suite now exposes Working Files under Review with a cycle kanban,
checklist cards labeled by accounting area, and a Balances tab. New files use the
52 check names and eight sections observed on the live Enterprise 2025 cycle.
Reviewers can mark checks Pending Review or Reviewed, add notes and multiple
supporting files per check, and use chatter. Existing single-file evidence remains
available for records created before multi-file evidence was added. Evidence upload
and removal are blocked after the working file is validated. The old generic starter
templates are archived, not deleted; administrator-created active templates remain
available and are added to future files. Existing working-file snapshots are not
rewritten when templates change. The list view remains available alongside the
cycle cards. A Spreadsheet tab now opens the native Odoo spreadsheet editor for
the working file. The workbook is stored on the record and autosaves after edits;
auditors and validated files open read-only. This uses the installed Community
`spreadsheet` model and editor component rather than the read-only dashboard
surface. The Spreadsheet tab now mounts the Odoo editor inside the working file,
alongside Cycles and Balances as in Enterprise. The existing full-screen open
action remains as an additional shortcut. A local browser tour verified that the
embedded editor loads, handles a cell update, reaches its Saved state, and
persists the edited value in the Odoo snapshot; it also verifies that the
full-screen shortcut still opens. A full page reload after saving has not yet
been exercised.
Accounting managers can validate or reopen a file, and validation is blocked
until every checklist item is reviewed. Company-scoped access is applied.

The Balances tab creates one line for each active account in the file's company.
It shows current-period balance, the corresponding prior-year balance,
variation, variation percentage, last comment, and review status, with account
type filters. Posted `account.move.line` data is used; accounts that carry
opening balances are calculated through the period end, while income and
expense accounts use the selected date range. A Refresh Accounts action adds
new company accounts without replacing comments or review statuses.

The balance arithmetic now has isolated posted-entry coverage: a balance-sheet
account carries its historical opening balance through the selected end date,
and a revenue account includes only activity inside the current and prior-year
periods. The fixture also verifies variation and percentage calculations. Both
tests pass on the local Odoo 20 database; this confirms the Community rules, not
numeric equality with the live Enterprise company's ledger.

Parity remains partial because browser save/reload has not yet been exercised.
Several Enterprise checklist prompts refer to Belgian
GAAP or account numbers 17/42; those
jurisdiction-specific instructions were observed in the Enterprise company and need
review before applying them to Egyptian entities. The live Enterprise balance table
had 52 accounts; the local company
has 50 active accounts and only two posted journal-item rows. The local balance
view therefore still needs a matched-period comparison against the Enterprise
ledger before numeric parity is established. The local database has no
fiscal-year records, so the
Community date range does not depend on a configured fiscal year.
