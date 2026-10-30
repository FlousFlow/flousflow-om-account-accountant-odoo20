from odoo import models


class ReportOpenItems(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.open_items_document'
    _description = 'Open Items Report'

    def _get_report_values(self, docids, data=None):
        return {
            'report_data': (data or {}).get('report_data', {}),
            'docs': self.env['account.move.line'].browse(docids),
        }
