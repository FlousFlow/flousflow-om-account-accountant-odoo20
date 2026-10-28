# Review Menu and Report Parity

Last live comparison: 2026-10-28

This ledger tracks the Community implementation against the FlousFlow Enterprise
Odoo 20 database. Menu names and report options are observations from the live
Review menu and report screens. Financial totals must be compared only on matched
company data and period.

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
Documents folder. The live record has Cycles, Balances, and Spreadsheet tabs;
its audit checklist contains 52 checks grouped by accounting area, with review
states, notes, evidence uploads, and activity history.

The Community suite now exposes a Working Files destination under Review. A
file is tied to a company and a user-entered date range and starts with a generic checklist;
reviewers can mark checks Pending Review or Reviewed, add notes and one evidence
attachment per check, and use chatter. Accounting managers can validate or
reopen a file, and validation is blocked until every check is reviewed. Company
rules and accounting-role access are applied. The starter checklist has 9
generic checks and is not the Enterprise 52-check template.

Parity remains partial: Cycles and balances are not implemented, there is no
Spreadsheet tab, the checklist taxonomy and depth differ, and evidence storage
supports one attachment per check rather than the observed Enterprise upload
workflow. Local runtime verification confirmed the Review menu, action,
empty-state list, and form load. The database has no fiscal-year records, so the
file uses explicit start/end dates rather than depending on configured fiscal
years. The new destination does not claim Enterprise parity for these gaps.
