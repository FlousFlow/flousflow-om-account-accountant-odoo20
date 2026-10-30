# Accounting Suite for Odoo 20 Community

An Odoo 20 accounting suite that brings reports, reconciliation, cash management,
assets, budgets, follow-up, and accounting dashboards into one Community
installation.

## Included workflows

- Financial statements, ledgers, aged balances, tax reports, open items, and
  partner statements.
- Bank and cash reconciliation, statement import, and internal transfers.
- Assets and depreciation, budgets, recurring entries, and fiscal-year controls.
- Customer follow-up, cash forecasting, currency updates, and revaluation.
- Vendor-bill data extraction and accounting dashboards.
- Working-file balance review and accounting menu configuration.

## Installation

1. Use Odoo 20.0 Community Edition.
2. Add this repository and the standard Odoo 20 addon paths to `addons_path`.
3. Restart Odoo and update the Apps list.
4. Install **Accounting Suite** (`om_account_accountant`). Its dependencies are
   included in this repository or provided by the standard Odoo 20 addons.

For on-premise PDF output, install the Odoo-compatible `wkhtmltopdf` build with
patched Qt. Vendor-bill OCR runs locally and requires Tesseract and Poppler on
the Odoo host. Currency-rate updates contact the provider selected by the
administrator when that feature is configured.

## Licensing and attribution

The root suite addon is LGPL-3. The repository contains separately licensed
components; check each addon's `__manifest__.py` before redistribution. In
particular, `ff_account_transfer` is OPL-1. Upstream contributor and copyright
notices are retained in the corresponding addon sources.

## Support

Contact [support@flousflow.com](mailto:support@flousflow.com).
