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

Enterprise exposes Working Files from Review. The local Community addon path
and development database have no Odoo Documents module. This requires a separate
local document-storage/integration decision; it is not currently represented
by an equivalent Review action.
