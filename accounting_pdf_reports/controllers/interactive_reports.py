import datetime

from odoo import fields, http
from odoo.http import request
from werkzeug.exceptions import Forbidden, NotFound


class InteractiveAccountingReports(http.Controller):
    """Authenticated, server-rendered report screens for the Community suite."""

    @http.route('/accounting_pdf_reports/financial_report', type='http', auth='user')
    def financial_report(self, report_id=None, date_from=None, date_to=None,
                        target_move='posted', journal_ids=None, **kwargs):
        if not request.env.user.has_group('account.group_account_readonly'):
            raise Forbidden()
        try:
            report_id = int(report_id)
        except (TypeError, ValueError):
            raise NotFound()
        report = request.env['account.financial.report'].browse(report_id).exists()
        allowed_reports = request.env.ref(
            'accounting_pdf_reports.account_financial_report_balancesheet0'
        ) | request.env.ref('accounting_pdf_reports.account_financial_report_profitandloss0')
        if not report or report not in allowed_reports:
            raise NotFound()
        if target_move not in ('posted', 'all'):
            target_move = 'posted'
        try:
            date_from = fields.Date.to_date(date_from) if date_from else False
            date_to = fields.Date.to_date(date_to) if date_to else fields.Date.context_today(request.env.user)
        except (TypeError, ValueError):
            date_from = False
            date_to = fields.Date.context_today(request.env.user)

        journals = request.env['account.journal'].search([
            ('company_id', 'child_of', request.env.company.id),
        ])
        if journal_ids:
            try:
                requested_ids = [int(value) for value in str(journal_ids).split(',') if value]
            except ValueError:
                requested_ids = []
            selected = journals.filtered(lambda journal: journal.id in requested_ids)
            if selected:
                journals = selected
        used_context = {
            'date_from': date_from,
            'date_to': date_to,
            'state': target_move,
            'strict_range': bool(date_from),
            'company_id': request.env.company.id,
            'journal_ids': journals.ids,
        }
        lines = request.env['report.accounting_pdf_reports.report_financial'].get_account_lines({
            'account_report_id': (report.id, report.name),
            'used_context': used_context,
            'enable_filter': False,
            'debit_credit': False,
        })
        draft_count = request.env['account.move'].search_count([
            ('state', '=', 'draft'),
            ('company_id', 'child_of', request.env.company.id),
            ('journal_id', 'in', journals.ids),
            *([('date', '>=', date_from)] if date_from else []),
            *([('date', '<=', date_to)] if date_to else []),
        ])
        pdf_action = request.env.ref(
            'accounting_pdf_reports.action_account_report_bs'
            if report == request.env.ref('accounting_pdf_reports.account_financial_report_balancesheet0')
            else 'accounting_pdf_reports.action_account_report_pl'
        )
        return request.render('accounting_pdf_reports.interactive_financial_report', {
            'report': report,
            'lines': lines,
            'date_from': date_from,
            'date_to': date_to,
            'target_move': target_move,
            'journals': journals,
            'draft_count': draft_count,
            'company': request.env.company,
            'pdf_action_id': pdf_action.id,
            'datetime': datetime,
            'context_timestamp': lambda value: fields.Datetime.context_timestamp(request.env.user, value),
        })
