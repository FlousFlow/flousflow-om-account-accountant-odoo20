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
comparison (including previous period), grouping by account, product category,
or product, options for all entries and hiding zero lines, a currency scale,
and print. The live screen currently has no rows. Deferred Revenues is also
available under Review.

The local suite has the `om_account_asset` asset and revenue-recognition board,
but no equivalent period-based interactive reports or Review entries. At the
time of comparison, the local database had zero assets, asset categories,
asset schedule moves, and invoice lines assigned to asset categories. The next
implementation must use the local asset recognition schedules and preserve
company currency, journal state, and company boundaries; an empty local result
alone cannot validate nonzero schedule arithmetic.

## Working Files

Enterprise exposes Working Files from Review. The local Community addon path
and development database have no Odoo Documents module. This requires a separate
local document-storage/integration decision; it is not currently represented
by an equivalent Review action.
