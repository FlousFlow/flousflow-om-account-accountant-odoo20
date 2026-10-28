from io import BytesIO

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError
from odoo.tools.binary import BinaryBytes
from odoo.tools.misc import format_date, get_lang


class AccountingReport(models.TransientModel):
    _name = "accounting.report"
    _inherit = "account.common.report"
    _description = "Accounting Report"

    @api.model
    def _get_account_report(self):
        reports = []
        if self.env.context.get('active_id'):
            menu = self.env['ir.ui.menu'].browse(self.env.context.get('active_id')).name
            reports = self.env['account.financial.report'].search([('name', 'ilike', menu)])
        return reports and reports[0] or False

    enable_filter = fields.Boolean(string='Enable Comparison')
    account_report_id = fields.Many2one('account.financial.report', string='Account Reports',
                                        required=True, default=_get_account_report)
    label_filter = fields.Char(string='Column Label', help="This label will be displayed on report to "
                                                           "show the balance computed for the given comparison filter.")
    filter_cmp = fields.Selection([('filter_no', 'No Filters'), ('filter_date', 'Date')],
                                  string='Filter by', required=True, default='filter_no')
    date_from_cmp = fields.Date(string='Date From')
    date_to_cmp = fields.Date(string='Date To')
    debit_credit = fields.Boolean(string='Display Debit/Credit Columns',
                                  help="This option allows you to get more details about "
                                       "the way your balances are computed."
                                       " Because it is space consuming, we do not allow to"
                                       " use it while doing a comparison.")
    xlsx_file = fields.Binary(attachment=False)
    xlsx_filename = fields.Char()
    comparison_period_ranges = fields.Json(default=list)
    comparison_sort = fields.Selection(
        [('ascending', 'Ascending'), ('descending', 'Descending')],
        default='descending',
    )
    comparison_display = fields.Selection(
        [('amount', 'Amount'), ('percentage', 'Percentage')],
        default='amount',
    )

    def _build_comparison_context(self, data):
        result = {}
        result['journal_ids'] = 'journal_ids' in data['form'] and data['form']['journal_ids'] or False
        result['state'] = 'target_move' in data['form'] and data['form']['target_move'] or ''
        # the comparison context replaces the main one, so it must carry the company
        # too, otherwise the comparison column spans every company of the switcher
        result['company_id'] = self.company_id.id or False
        if data['form']['filter_cmp'] == 'filter_date':
            result['date_from'] = data['form']['date_from_cmp']
            result['date_to'] = data['form']['date_to_cmp']
            result['strict_range'] = True
        return result

    def check_report(self):
        res = super().check_report()
        data = {'form': self.read([
            'account_report_id', 'date_from_cmp', 'date_to_cmp', 'journal_ids',
            'filter_cmp', 'target_move', 'comparison_period_ranges',
            'comparison_sort', 'comparison_display', 'enable_filter',
        ])[0]}
        for field in ['account_report_id']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        comparison_context = self._build_comparison_context(data)
        res['data']['form'].update(data['form'])
        res['data']['form']['comparison_context'] = comparison_context
        return res

    def _print_report(self, data):
        data['form'].update(self.read([
            'date_from_cmp', 'debit_credit', 'date_to_cmp', 'filter_cmp',
            'account_report_id', 'enable_filter', 'label_filter', 'target_move',
            'comparison_period_ranges', 'comparison_sort', 'comparison_display',
        ])[0])
        return self.env.ref('accounting_pdf_reports.action_report_financial').report_action(
            self, data=data, config=False)

    def _get_interactive_report_data(self, form):
        self.ensure_one()
        report_value = form['account_report_id']
        report_id = report_value[0] if isinstance(report_value, (list, tuple)) else report_value

        def normalize_date(value):
            if not value:
                return False
            return value if isinstance(value, str) else fields.Date.to_string(value)

        return self.env['report.accounting_pdf_reports.report_financial'].get_interactive_data(
            report_id,
            normalize_date(form.get('date_from')),
            normalize_date(form.get('date_to')),
            form.get('target_move') or 'posted',
            form.get('journal_ids') or [],
            bool(form.get('enable_filter')),
            bool(form.get('debit_credit')),
            form.get('comparison_context'),
            comparison_period_ranges=form.get('comparison_period_ranges') or None,
        )

    def _prepare_export_data(self, form, report_data):
        self.ensure_one()
        comparison_contexts = report_data.get('comparison_contexts') or []
        balance_sheet = self.env.ref('accounting_pdf_reports.account_financial_report_balancesheet0')
        report_value = form.get('account_report_id')
        report_id = report_value[0] if isinstance(report_value, (list, tuple)) else report_value

        def period_label(date_from, date_to, current=False):
            if current and report_id == balance_sheet.id:
                return _('Balance')
            start = fields.Date.to_date(date_from) if date_from else False
            end = fields.Date.to_date(date_to) if date_to else False
            if start and end:
                return f"{format_date(self.env, start)} – {format_date(self.env, end)}"
            if end:
                return f"{_('As of')} {format_date(self.env, end)}"
            if start:
                return f"{_('From')} {format_date(self.env, start)}"
            return _('Balance')

        columns = [{
            'key': 'current', 'index': -1, 'current': True,
            'date_from': form.get('date_from') or False,
            'date_to': form.get('date_to') or False,
            'label': period_label(form.get('date_from'), form.get('date_to'), current=True),
        }]
        columns.extend({
            'key': f'comparison-{index}', 'index': index, 'current': False,
            'date_from': context.get('date_from') or False,
            'date_to': context.get('date_to') or False,
            'label': period_label(context.get('date_from'), context.get('date_to')),
        } for index, context in enumerate(comparison_contexts))
        columns.sort(
            key=lambda column: fields.Date.to_string(fields.Date.to_date(
                column['date_from'] or column['date_to']
            )) if column['date_from'] or column['date_to'] else '',
            reverse=form.get('comparison_sort', 'descending') != 'ascending',
        )
        show_change = bool(form.get('enable_filter')) and len(comparison_contexts) == 1
        comparison_display = form.get('comparison_display', 'amount')
        for line in report_data['lines']:
            line['comparison_change'] = False
            if not show_change:
                continue
            current = float(line.get('balance') or 0.0)
            previous = float((line.get('balance_cmp_list') or [line.get('balance_cmp') or 0.0])[0])
            if comparison_display == 'percentage':
                if abs(previous) < 0.005:
                    line['comparison_change'] = '0.00%' if abs(current) < 0.005 else _('N/A')
                else:
                    line['comparison_change'] = f"{((current - previous) / abs(previous) * 100):.2f}%"
            else:
                line['comparison_change'] = current - previous
        return {
            **report_data,
            'period_columns': columns,
            'show_comparison_change': show_change,
            'comparison_display': comparison_display,
            'comparison_change_label': (
                _('Change (%)') if comparison_display == 'percentage' else _('Change')
            ),
        }

    def action_export_xlsx(self):
        self.ensure_one()
        if not self.env.user.has_group('account.group_account_readonly'):
            raise AccessError(_('You are not allowed to read accounting reports.'))
        try:
            import xlsxwriter
        except ImportError as error:
            raise UserError(_('Excel export requires the XlsxWriter package.')) from error

        form = self.read([
            'date_from', 'date_to', 'journal_ids', 'target_move', 'company_id',
            'account_report_id', 'date_from_cmp', 'date_to_cmp', 'filter_cmp',
            'enable_filter', 'label_filter', 'debit_credit',
            'comparison_period_ranges', 'comparison_sort', 'comparison_display',
        ])[0]
        if self.enable_filter:
            form['comparison_context'] = self._build_comparison_context({'form': form})
        report = self.account_report_id
        report_data = self._prepare_export_data(form, self._get_interactive_report_data(form))
        lines = report_data['lines']

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(_('Financial Report'))
        sheet.right_to_left() if get_lang(self.env).code.startswith('ar') else None
        title_format = workbook.add_format({'bold': True, 'font_size': 15})
        meta_format = workbook.add_format({'font_color': '#666666'})
        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#D8DEE7', 'bottom': 1,
        })
        number_format = workbook.add_format({'num_format': '#,##0.00;[Red]-#,##0.00'})
        bold_number_format = workbook.add_format({
            'bold': True, 'num_format': '#,##0.00;[Red]-#,##0.00',
        })
        name_formats = [workbook.add_format({'indent': level}) for level in range(16)]
        bold_name_formats = [workbook.add_format({'bold': True, 'indent': level}) for level in range(16)]
        right_text_format = workbook.add_format({'align': 'right'})
        bold_right_text_format = workbook.add_format({'bold': True, 'align': 'right'})

        sheet.merge_range(0, 0, 0, 1, report.display_name, title_format)
        sheet.write(1, 0, _('Company'), meta_format)
        sheet.write(1, 1, self.company_id.display_name, meta_format)
        sheet.write(2, 0, _('Target Moves'), meta_format)
        sheet.write(2, 1, _('All Posted Entries') if self.target_move == 'posted' else _('All Entries'), meta_format)
        if self.date_from or self.date_to:
            sheet.write(3, 0, _('Period'), meta_format)
            sheet.write(3, 1, ' - '.join(str(value) for value in (self.date_from, self.date_to) if value), meta_format)

        headers = [_('Account')]
        if self.debit_credit:
            headers.extend([_('Debit'), _('Credit')])
        headers.extend(column['label'] for column in report_data['period_columns'])
        if report_data['show_comparison_change']:
            headers.append(report_data['comparison_change_label'])
        header_row = 5 if self.date_from or self.date_to else 4
        for column, label in enumerate(headers):
            sheet.write(header_row, column, label, header_format)

        for row_index, line in enumerate((row for row in lines if row.get('level') != 0), header_row + 1):
            level = max(0, min(int(line.get('level', 0)), 15))
            bold = line.get('type') == 'report' or level <= 2
            show_amount = line.get('show_amount', True)
            sheet.write(row_index, 0, line.get('name', ''),
                        bold_name_formats[level] if bold else name_formats[level])
            column = 1
            if self.debit_credit:
                for field_name in ('debit', 'credit'):
                    if show_amount:
                        sheet.write_number(row_index, column, line.get(field_name, 0.0),
                                           bold_number_format if bold else number_format)
                    else:
                        sheet.write_blank(row_index, column, None)
                    column += 1
            for period_column in report_data['period_columns']:
                if period_column['current']:
                    amount = line.get('balance', 0.0)
                else:
                    amounts = line.get('balance_cmp_list') or [line.get('balance_cmp', 0.0)]
                    amount = amounts[period_column['index']] if period_column['index'] < len(amounts) else 0.0
                if show_amount:
                    sheet.write_number(row_index, column, amount,
                                       bold_number_format if bold else number_format)
                else:
                    sheet.write_blank(row_index, column, None)
                column += 1
            if report_data['show_comparison_change']:
                change = line.get('comparison_change')
                if not show_amount:
                    sheet.write_blank(row_index, column, None)
                elif report_data['comparison_display'] == 'percentage' or isinstance(change, str):
                    sheet.write(row_index, column, change,
                                bold_right_text_format if bold else right_text_format)
                else:
                    sheet.write_number(row_index, column, change,
                                       bold_number_format if bold else number_format)
                column += 1

        sheet.set_column(0, 0, 52)
        sheet.set_column(1, len(headers) - 1, 18)
        workbook.close()
        filename = f"{report.name.replace('/', '-')}.xlsx"
        self.write({
            'xlsx_file': BinaryBytes(output.getvalue(), filename=filename),
            'xlsx_filename': filename,
        })
        return {
            'type': 'ir.actions.act_url',
            'url': (
                f'/web/content?model={self._name}&id={self.id}'
                '&field=xlsx_file&filename_field=xlsx_filename&download=true'
            ),
            'target': 'self',
        }
