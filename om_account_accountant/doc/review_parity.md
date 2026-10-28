# Review Menu and Report Parity

Last live comparison: 2026-10-28

This ledger tracks the Community implementation against the FlousFlow Enterprise
Odoo 20 database. Menu names and report options are observations from the live
Review menu and report screens. Financial totals must be compared only on matched
company data and period.

The local Review menu now follows the live grouping and order: Audit (Working
Files, Annual Report), Inventory, Regulatory (Unrealized Currencies, Deferred
Revenues, Deferred Expenses), Purchases, then Sales.

## Journal Audit

| Capability | Enterprise | Community | Status |
| --- | --- | --- | --- |
| Review menu entry and interactive report | Yes | Yes | Implemented |
| Period, posted/draft/all entries | Year selector; posted, draft, or all | Year selector; posted, draft, or all | Implemented |
| Include payments | Yes | Yes | Implemented |
| Display scale | Currency, thousands, millions | Currency, thousands, millions | Implemented |
| Journal totals and expandable entries | Yes | Yes | Implemented |
| Review action | Marks entries reviewed | Calls Odoo's native `set_moves_checked` for eligible posted entries | Implemented; no entry was changed during verification |
| Tax summary and drill-down | Yes | Yes | Implemented |
| Print | Yes | Yes | Implemented |
| XLSX export | Yes | Yes; Journals, Entries, and Taxes worksheets | Implemented and downloaded/validated |
| Send to Documents | Yes | No Documents module in the local addon path/database | Remaining platform integration |
| Insert in Article | Yes | No equivalent Knowledge integration in the local addon path/database | Remaining platform integration |

The live Enterprise report showed three entries awaiting review and a nonzero
Purchases balance. The local development database showed one posted
Miscellaneous Operations entry with no review pending and zero balance. These
are different databases and are not evidence of a report-calculation mismatch.

## Deferred Expenses and Deferred Revenues

The live Deferred Expenses report has a monthly period selector, period
comparison (none or a selected number of previous periods), ascending or
descending ordering, comparison by amount or percentage, grouping by account,
product category, or product, options for all entries and hiding zero lines, a
currency scale, and print. The live screen currently has no rows. Deferred
Revenues is also available under Review.

The local suite has `om_account_asset` asset and revenue-recognition boards.
Review now exposes separate Deferred Expenses and Deferred Revenues interactive
reports. They use the monthly asset schedule moves and their actual recognition
account lines, with posted/all entries, account/category/product grouping,
the journal selector, a selected count of previous-month comparisons, amount or
percentage changes, ascending/descending ordering, hide-zero, company-currency
scaling, print, and drill-down to the matching journal entries. Their XLSX
export includes Schedule and Entries worksheets and preserves comparison
filters. New assets retain their source invoice line so product grouping can
use the actual product.

Remaining differences: the Community report compares the current month with
consecutive previous months; a distinct custom comparison-date range has not
been implemented. Existing assets created before the source-invoice-line field
was added have no product link and fall back to the asset name for product
grouping. The Enterprise options to send the report to Documents or insert it
into an article are not available locally. At the time of comparison, the local
database had zero assets, asset categories, asset schedule moves, and invoice
lines assigned to asset categories. The live Enterprise report also had no
rows, so nonzero schedule arithmetic has not yet been validated against matched
records.

## Working Files

Enterprise exposes Working Files from Review as an audit dossier, not as a
Documents folder. The current live cycle screen exposes Cycle and Balances
navigation. Its audit checklist contains 52 checks grouped by accounting area,
with review states, notes, evidence uploads, and activity history. A Spreadsheet
tab was not visible in the selected cycle detail, so its Enterprise location and
behavior remain unverified.

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
cycle cards. Spreadsheet parity remains unverified until the Enterprise surface
that exposes it is identified.
Accounting managers can validate or reopen a file, and validation is blocked
until every checklist item is reviewed. Company-scoped access is applied.

The Balances tab creates one line for each active account in the file's company.
It shows current-period balance, the corresponding prior-year balance,
variation, variation percentage, last comment, and review status, with account
type filters. Posted `account.move.line` data is used; accounts that carry
opening balances are calculated through the period end, while income and
expense accounts use the selected date range. A Refresh Accounts action adds
new company accounts without replacing comments or review statuses.

Parity remains partial because Spreadsheet behavior is unverified. Several
Enterprise checklist prompts refer to Belgian GAAP or account numbers 17/42; those
jurisdiction-specific instructions were observed in the Enterprise company and need
review before applying them to Egyptian entities. The live Enterprise balance table
had 52 accounts; the local company
has 50 active accounts and only two posted journal-item rows. Its balance view
therefore needs a non-zero fixture and matched-period comparison before numeric
parity is established. The local database has no fiscal-year records, so the
Community date range does not depend on a configured fiscal year.
