# Odoo Enterprise Accounting Parity

Scope: compare the FlousFlow Odoo 20 Community accounting database and module with the connected Enterprise accounting database. This is a living gap register, not a claim of full parity.

Last reviewed: 2026-10-29

## Verified comparison

| Requirement | Enterprise support | Local evidence | Actual gap | Next step |
| --- | --- | --- | --- | --- |
| Review menu destinations | Review exposes Control, Audit, Inventory, Regulatory, Purchases, and Sales destinations, including Journal Items, Audit Trail, Journal Audit, Working Files, Annual Report, Inventory Valuation, Unrealized Currencies, Deferred Revenues/Expenses, Bills To Receive, Billed Not Received, Invoices To Be Issued, and Invoiced Not Delivered. | Browser menu on the local 8077 database showed the same groups and destinations. `om_account_accountant/views/review_menu.xml` defines the corresponding actions and menus. | No menu-entry gap was observed. This verifies visible destinations only; it does not prove equal behavior or permissions for every user. | Continue checking the destination view and workflow for each Review item, starting with Journal Audit and the accrual queues. |
| Working File review checklist | Enterprise Working Files shows sectioned review cards with notes, evidence upload, per-check status, reviewer activity, and a spreadsheet tab. The inspected file had 52 checks. | The local implementation has checklist, evidence, status, reviewer fields, balances, and spreadsheet views. The local database contains 52 check templates and 52 checks on its active file. | Checklist count is aligned. Local UI side-by-side verification was interrupted by an expired login; the local file's completion state and content are data-dependent and were not compared to the Enterprise file. | Re-authenticate and compare checklist interactions, evidence uploads, status transitions, spreadsheet integration, and balance review against the Enterprise record. |
| Bills To Receive accrual queue | Enterprise shows an as-of date, a 365-day filter, vendor grouping, order/product columns, received and billed quantities, unit price, and amount. The live report displayed grouped totals by vendor. | Local XML defines the same columns, grouping/filter context, and `review_accrual_list` date control; local Python passes the selected as-of date to native Odoo accrual calculations. | Source-level behavior matches these visible controls, but local runtime view and grouped totals were not rechecked after the session expired. | Re-authenticate and verify the date picker, vendor grouping, totals, and historical quantities in the local view. |
| Financial formula details | Balance Sheet rows expose an info control whose tooltip shows Engine, Label, Formula, and Value. The Current Assets example showed `BA.balance + REC.balance + CAS.balance + PRE.balance`. | The local Balance Sheet showed the same info control; its tooltip displayed the same engine, label, formula, and value. | No formula-tooltip gap was observed for the checked row. | Check additional formula types and the P&L report before claiming report-wide parity. |
| Report action menu | On the Enterprise Balance Sheet, the settings menu showed XLSX, Send to Documents, and Insert in Article. | The local Balance Sheet report action menu showed XLSX only. The local runtime has no `documents` addon in the Odoo 20 addons tree; `knowledge` is marked uninstallable. | Send to Documents and Insert in Article are missing and depend on Enterprise apps that are not available in this Community runtime. Adding UI-only placeholders would not provide the workflows. | Keep these as Enterprise-only gaps until the corresponding supported apps/APIs are available or an approved Community alternative is chosen. |
| P&L selected-budget parity | Enterprise P&L exposes a searchable Budget selector with a Create action. | `accounting_pdf_reports` 2.0.23 now provides a searchable dropdown, filters existing budgets as the user types, allows clearing the selection, and opens the existing create-budget dialog prefilled from the search text. Existing budget selection still reloads the report. Backend calculation/export tests passed on an isolated database; module upgrade also succeeded on the primary local development database. | The local browser session is still unauthenticated, so visual behavior and keyboard/dropdown interaction have not yet been confirmed in the running UI. Enterprise budget creation semantics and date-range allocation have not been fully compared. | Re-authenticate the local browser session; compare the selector interaction, create flow, date-range allocation, and printed/exported values against Enterprise before calling this area matched. |

## Evidence boundaries

- Enterprise evidence came from the connected `edu-flousflow.odoo.com` browser tab on 2026-10-29.
- Local UI evidence came from `http://127.0.0.1:8077` before its browser session expired. The local Odoo database is `flousflow_om_accountant_dev20_20261028`.
- Report balances differ between databases and are not treated as a parity defect without matched accounting data, company, date, and report filters.
- The Review menu comparison does not establish ACL or record-rule parity.

## Current implementation state

- Local branch: `20.0`.
- `om_account_accountant`: installed, `20.0.1.33.0`.
- `accounting_pdf_reports`: installed, `20.0.2.0.23` (upgraded on 2026-10-29).
- Remaining differences are tracked above; parity is incomplete.
