from io import BytesIO

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError
from odoo.tools.binary import BinaryBytes
from odoo.tools.misc import get_lang


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
        data = {}
        data['form'] = self.read(['account_report_id', 'date_from_cmp', 'date_to_cmp', 'journal_ids',
                                  'filter_cmp', 'target_move'])[0]
        for field in ['account_report_id']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        comparison_context = self._build_comparison_context(data)
        res['data']['form']['comparison_context'] = comparison_context
        return res

    def _print_report(self, data):
        data['form'].update(self.read(['date_from_cmp', 'debit_credit', 'date_to_cmp', 'filter_cmp',
                                       'account_report_id', 'enable_filter', 'label_filter', 'target_move'])[0])
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
        )

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
        ])[0]
        if self.enable_filter:
            form['comparison_context'] = self._build_comparison_context({'form': form})
        report = self.account_report_id
        report_data = self._get_interactive_report_data(form)
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
        headers.append(_('Balance'))
        if self.enable_filter:
            headers.append(self.label_filter or _('Comparison'))
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
            for field_name in ('balance', 'balance_cmp'):
                if field_name == 'balance_cmp' and not self.enable_filter:
                    continue
                if show_amount:
                    sheet.write_number(row_index, column, line.get(field_name, 0.0),
                                       bold_number_format if bold else number_format)
                else:
                    sheet.write_blank(row_index, column, None)
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
