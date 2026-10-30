# FlousFlow Community Accounting Suite — Odoo 20

This repository contains the uploaded `om_account_accountant-20.0.1.4.0`
Community accounting suite. The root application is
`om_account_accountant`; its sibling addons are kept together because the
root manifest depends on them.

The root display name is branded **FlousFlow Community Accounting Suite**.
The technical addon names remain unchanged so the suite's dependency graph,
XML IDs, migrations, and Odoo 20 integrations remain valid.

## Foundation modules

The suite includes accounting reports, assets, budgets, fiscal years, recurring
payments, follow-up, reconciliation, cash forecast, bank statement import,
currency revaluation/rate update, cheque printing, OCR, and spreadsheet
dashboards.

## Standalone installation

The root addon and its FlousFlow addon dependencies are packaged in this
repository. Install it with the standard Odoo 20 Community addon paths and this
repository in `addons_path`, then install `om_account_accountant`. Its
dependency graph uses the bundled FlousFlow addons and standard Odoo 20 addons;
it does not require Odoo Enterprise's `account_accountant` addon.

A clean install of `om_account_accountant` and its dependencies completed on
Odoo 20 in database `ff_om_accountant_independence_20261030`. The installed
suite contains 96 modules, including the root addon, accounting reports,
transfer, branch analytics, and the standard accounting spreadsheet dashboard.

## PDF report rendering

The `accounting_pdf_reports` addon uses Odoo's server-side PDF renderer. On
on-premise installations, install the Odoo-compatible `wkhtmltopdf` 0.12.6
build with patched Qt on the Odoo host; it is an operating-system dependency,
not a Python package or addon payload. See
[`accounting_pdf_reports/README.md`](accounting_pdf_reports/README.md) for
installation and verification notes, including Apple Silicon limitations.

## Verification database

The clean Odoo 20 installation verification database is
`ff_om_accountant_independence_20261030`.
