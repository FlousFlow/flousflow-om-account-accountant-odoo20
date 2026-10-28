import time
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.orm.domains import Domain


class ReportFinancial(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.report_financial'
    _description = 'Financial Reports'

    def _compute_account_balance(self, accounts):
        """ compute the balance, debit and credit for the provided accounts
        """
        mapping = {
            'balance': "COALESCE(SUM(debit),0) - COALESCE(SUM(credit), 0) as balance",
            'debit': "COALESCE(SUM(debit), 0) as debit",
            'credit': "COALESCE(SUM(credit), 0) as credit",
        }

        res = {}
        for account in accounts:
            res[account.id] = dict.fromkeys(mapping, 0.0)
        if accounts:
            # the query below reads the journal items from the database
            self.env['account.move.line'].flush_model()
            tables, where_clause, where_params = self.env['account.move.line']._query_get()
            tables = tables.replace('"', '') if tables else "account_move_line"
            wheres = [""]
            if where_clause.strip():
                wheres.append(where_clause.strip())
            filters = " AND ".join(wheres)
            request = "SELECT account_id as id, " + ', '.join(mapping.values()) + \
                       " FROM " + tables + \
                       " WHERE account_id IN %s " \
                            + filters + \
                       " GROUP BY account_id"
            params = (tuple(accounts._ids),) + tuple(where_params)
            self.env.cr.execute(request, params)
            for row in self.env.cr.dictfetchall():
                res[row['id']] = row
        return res

    def _compute_report_balance(self, reports):
        '''returns a dictionary with key=the ID of a record and value=the credit, debit and balance amount
           computed for this record. If the record is of type :
               'accounts' : it's the sum of the linked accounts
               'account_type' : it's the sum of leaf accoutns with such an account_type
               'account_report' : it's the amount of the related report
               'sum' : it's the sum of the children of this record (aka a 'view' record)'''
        res = {}
        fields = ['credit', 'debit', 'balance']
        for report in reports:
            if report.id in res:
                continue
            res[report.id] = dict((fn, 0.0) for fn in fields)
            if report.type == 'accounts':
                # it's the sum of the linked accounts
                res[report.id]['account'] = self._compute_account_balance(report.account_ids)
                for value in res[report.id]['account'].values():
                    for field in fields:
                        res[report.id][field] += value.get(field)
            elif report.type == 'account_type':
                # it's the sum the leaf accounts with such an account type
                accounts = self.env['account.account'].search(
                    [('account_type', 'in', report.account_type_ids.mapped('type'))])

                res[report.id]['account'] = self._compute_account_balance(accounts)
                for value in res[report.id]['account'].values():
                    for field in fields:
                        res[report.id][field] += value.get(field)
            elif report.type == 'account_report' and report.account_report_id:
                # it's the amount of the linked report
                res2 = self._compute_report_balance(report.account_report_id)
                for key, value in res2.items():
                    for field in fields:
                        res[report.id][field] += value[field]
            elif report.type == 'sum':
                # it's the sum of the children of this account.report
                res2 = self._compute_report_balance(report.children_ids)
                for key, value in res2.items():
                    for field in fields:
                        res[report.id][field] += value[field]
        return res

    def get_account_lines(self, data):
        lines = []
        account_report = self.env['account.financial.report'].search(
            [('id', '=', data['account_report_id'][0])])
        child_reports = account_report._get_children_by_order()
        res = self.with_context(data.get('used_context'))._compute_report_balance(child_reports)
        if data['enable_filter']:
            comparison_res = self.with_context(
                data.get('comparison_context'))._compute_report_balance(
                child_reports)
            for report_id, value in comparison_res.items():
                res[report_id]['comp_bal'] = value['balance']
                report_acc = res[report_id].get('account')
                if report_acc:
                    for account_id, val in comparison_res[report_id].get('account').items():
                        report_acc[account_id]['comp_bal'] = val['balance']
        for report in child_reports:
            vals = {
                'report_id': report.id,
                'name': report.name,
                'balance': res[report.id]['balance'] * float(report.sign),
                'type': 'report',
                # the style is a selection of strings: '0' is the automatic formatting, i.e. the level in the tree
                'level': int(report.style_overwrite or 0) or report.level,
                'account_type': report.type or False, #used to underline the financial report balances
            }
            if data['debit_credit']:
                vals['debit'] = res[report.id]['debit']
                vals['credit'] = res[report.id]['credit']

            if data['enable_filter']:
                vals['balance_cmp'] = res[report.id]['comp_bal'] * float(report.sign)

            lines.append(vals)
            if report.display_detail == 'no_detail':
                #the rest of the loop is used to display the details of the financial report, so it's not needed here.
                continue
            if res[report.id].get('account'):
                sub_lines = []
                for account_id, value in res[report.id]['account'].items():
                    #if there are accounts to display, we add them to the lines with a level equals to their level in
                    #the COA + 1 (to avoid having them with a too low level that would conflicts with the level of data
                    #financial reports for Assets, liabilities...)
                    flag = False
                    account = self.env['account.account'].browse(account_id)
                    vals = {
                        'name': ' '.join(part for part in (account.code, account.name) if part),
                        'account_id': account.id,
                        'balance': value['balance'] * float(report.sign) or 0.0,
                        'type': 'account',
                        # must never be False: the template skips rows whose level is 0/False
                        'level': 4 if report.display_detail == 'detail_with_hierarchy' else report.level + 1,
                        'account_type': account.account_type,
                        'non_trade': account.non_trade,
                    }
                    if data['debit_credit']:
                        vals['debit'] = value['debit']
                        vals['credit'] = value['credit']
                        if (not self.env.company.currency_id.is_zero(vals['debit'])
                                or not self.env.company.currency_id.is_zero(vals['credit'])):
                            flag = True
                    if not self.env.company.currency_id.is_zero(vals['balance']):
                        flag = True
                    if data['enable_filter']:
                        vals['balance_cmp'] = value['comp_bal'] * float(report.sign)
                        if not self.env.company.currency_id.is_zero(vals['balance_cmp']):
                            flag = True
                    if flag:
                        sub_lines.append(vals)
                lines += sorted(sub_lines, key=lambda sub_line: sub_line['name'])
        return lines

    @api.model
    def get_interactive_period_dates(self, report_id, period_type, anchor_date):
        """Return dates for a supported Profit and Loss period preset."""
        if not self.env.user.has_group('account.group_account_readonly'):
            from odoo.exceptions import AccessError
            raise AccessError(_('You are not allowed to read accounting reports.'))
        report = self.env['account.financial.report'].browse(int(report_id)).exists()
        profit_loss = self.env.ref('accounting_pdf_reports.account_financial_report_profitandloss0')
        if report != profit_loss:
            from odoo.exceptions import AccessError
            raise AccessError(_('This period selector is only available for Profit and Loss.'))

        anchor = fields.Date.to_date(anchor_date) if anchor_date else fields.Date.context_today(self)
        if period_type == 'month':
            date_from = anchor + relativedelta(day=1)
            date_to = anchor + relativedelta(day=31)
        elif period_type == 'quarter':
            quarter_month = ((anchor.month - 1) // 3) * 3 + 1
            date_from = anchor.replace(month=quarter_month, day=1)
            date_to = date_from + relativedelta(months=3, days=-1)
        elif period_type == 'fiscal_year':
            dates = self.env.company.compute_fiscalyear_dates(anchor)
            date_from, date_to = dates['date_from'], dates['date_to']
        else:
            raise UserError(_('Unsupported report period.'))
        return {'date_from': fields.Date.to_string(date_from), 'date_to': fields.Date.to_string(date_to)}

    @api.model
    def get_interactive_data(self, report_id, date_from, date_to, target_move='posted',
                             journal_ids=None, comparison=False, debit_credit=False,
                             comparison_context=None, period_type=None,
                             comparison_mode='previous_period', comparison_date_from=None,
                             comparison_date_to=None):
        """Return the native financial-report hierarchy for the Odoo web client."""
        if not self.env.user.has_group('account.group_account_readonly'):
            from odoo.exceptions import AccessError
            raise AccessError(_('You are not allowed to read accounting reports.'))
        report = self.env['account.financial.report'].browse(int(report_id)).exists()
        allowed = self.env.ref('accounting_pdf_reports.account_financial_report_balancesheet0') | self.env.ref(
            'accounting_pdf_reports.account_financial_report_profitandloss0')
        if not report or report not in allowed:
            from odoo.exceptions import AccessError
            raise AccessError(_('This report is not available.'))
        company = self.env.company
        profit_loss = self.env.ref('accounting_pdf_reports.account_financial_report_profitandloss0')
        if report == profit_loss and not date_from and not date_to:
            fiscal_dates = company.compute_fiscalyear_dates(fields.Date.context_today(self))
            date_from, date_to = fiscal_dates['date_from'], fiscal_dates['date_to']
        journals = self.env['account.journal'].search([
            ('company_id', 'child_of', company.id),
        ])
        if journal_ids is not None and journal_ids is not False:
            requested = {int(journal_id) for journal_id in journal_ids}
            journals = journals.filtered(lambda journal: journal.id in requested)
        context = {
            'date_from': date_from or False,
            'date_to': date_to or False,
            'state': 'all' if target_move == 'all' else 'posted',
            'strict_range': bool(date_from),
            'company_id': company.id,
            'journal_ids': journals.ids,
        }
        data = {
            'account_report_id': (report.id, report.display_name),
            'used_context': context,
            'enable_filter': bool(comparison),
            'debit_credit': bool(debit_credit),
        }
        if comparison and comparison_context is not None:
            data['comparison_context'] = comparison_context
        elif comparison:
            start = fields.Date.to_date(date_from) if date_from else False
            end = fields.Date.to_date(date_to) if date_to else fields.Date.context_today(self)
            if comparison_mode == 'custom':
                comparison_start = fields.Date.to_date(comparison_date_from) if comparison_date_from else False
                comparison_end = fields.Date.to_date(comparison_date_to) if comparison_date_to else False
                if not comparison_start or not comparison_end or comparison_start > comparison_end:
                    raise UserError(_('Select a valid comparison date range.'))
            elif start:
                if comparison_mode == 'same_period_last_year':
                    comparison_start = start - relativedelta(years=1)
                    comparison_end = end - relativedelta(years=1)
                elif period_type == 'fiscal_year' or (start.month == 1 and start.day == 1 and period_type is None):
                    comparison_start = start - relativedelta(years=1)
                    comparison_end = end - relativedelta(years=1)
                else:
                    days = (end - start).days + 1
                    comparison_start = start - relativedelta(days=days)
                    comparison_end = start - relativedelta(days=1)
            else:
                comparison_start = False
                comparison_end = end - relativedelta(years=1)
            if comparison_start:
                data['comparison_context'] = dict(context, date_from=comparison_start.isoformat(),
                                                  date_to=comparison_end.isoformat(), strict_range=True)
            else:
                data['comparison_context'] = dict(
                    context, date_from=False, date_to=(end - relativedelta(years=1)).isoformat(),
                )
        hidden_wrapper = self.env.ref('accounting_pdf_reports.account_financial_report_liabilitysum0')
        current_asset_types = {'asset_cash', 'asset_receivable', 'asset_current', 'asset_prepayments'}
        fixed_asset_types = {'asset_fixed', 'asset_non_current'}
        current_liability_types = {'liability_current', 'liability_credit_card', 'liability_payable'}

        def account_domain_for_types(types):
            domains = []
            ordinary_types = set(types)
            special_domains = {
                'asset_receivable': [('account_type', '=', 'asset_receivable'), ('non_trade', '=', False)],
                'asset_current': Domain.OR([
                    [('account_type', '=', 'asset_current')],
                    [('account_type', '=', 'asset_receivable'), ('non_trade', '=', True)],
                ]),
                'liability_current': Domain.OR([
                    [('account_type', '=', 'liability_current')],
                    [('account_type', '=', 'liability_payable'), ('non_trade', '=', True)],
                ]),
                'liability_payable': [('account_type', '=', 'liability_payable'), ('non_trade', '=', False)],
            }
            for account_type, domain in special_domains.items():
                if account_type in ordinary_types:
                    domains.append(domain)
                    ordinary_types.remove(account_type)
            if ordinary_types:
                domains.append([('account_type', 'in', list(ordinary_types))])
            return Domain.AND([
                Domain.OR(domains),
                [('company_ids', 'child_of', company.id)],
            ])

        def account_ids_for_types(types):
            return self.env['account.account'].search(account_domain_for_types(types)).ids

        def amount_row(name, row_type, row_key, level, accounts, show_amount=True,
                       extra_account_ids=()):
            values = {
                field: sum(account.get(field, 0.0) for account in accounts)
                for field in ('debit', 'credit', 'balance', 'balance_cmp')
            }
            account_ids = set()
            for account in accounts:
                if account.get('account_id'):
                    account_ids.add(account['account_id'])
                account_ids.update(account.get('account_ids', []))
            account_ids.update(extra_account_ids)
            return {
                'name': name, 'type': row_type, 'row_key': row_key, 'level': level,
                'show_amount': show_amount,
                'account_ids': sorted(account_ids),
                **values,
            }

        def add_formula_info(line):
            """Expose the calculation behind a report line for its info popover."""
            row_key = line.get('row_key', '')
            row_type = line.get('type')
            report_formula_by_id = {
                self.env.ref('accounting_pdf_reports.account_financial_report_assets0').id:
                    'CA.balance + FA.balance + PNCA.balance',
                self.env.ref('accounting_pdf_reports.account_financial_report_balancesheet0').id:
                    'L.balance + EQ.balance',
                self.env.ref('accounting_pdf_reports.account_financial_report_liability0').id:
                    'CL.balance + NL.balance',
                self.env.ref('accounting_pdf_reports.account_financial_report_equity0').id:
                    'EQU.balance + EAR.balance + OCI.balance',
            }
            aggregate_formulas = {
                'asset-current-': 'BA.balance + REC.balance + CAS.balance + PRE.balance',
                'asset-total-current-': 'BA.balance + REC.balance + CAS.balance + PRE.balance',
                'asset-total-': 'CA.balance + FA.balance + PNCA.balance',
                'liability-current-': 'CL1.balance + CL2.balance + CL3.balance',
                'liability-total-current-': 'CL1.balance + CL2.balance + CL3.balance',
                'liability-total-': 'CL.balance + NL.balance',
                'earnings-': 'PYE.balance + CYE.balance',
                'equity-accounts-': "[('account_id.account_type', '=', 'equity')]",
                'current-year-earnings-': "[('account_id.account_type', 'in', ['income', 'income_other', 'expense_direct_cost', 'expense', 'expense_depreciation', 'expense_other'])]",
                'previous-years-earnings-': "[('account_id.account_type', 'in', ['income', 'income_other', 'expense_direct_cost', 'expense', 'expense_depreciation', 'expense_other', 'equity_unaffected'])]",
                'earnings-total-': 'PYE.balance + CYE.balance',
                'equity-total-': 'EQU.balance + EAR.balance + OCI.balance',
                'liabilities-equity-total-': 'L.balance + EQ.balance',
            }
            formula = next((value for prefix, value in aggregate_formulas.items()
                            if row_key.startswith(prefix)), None)
            if not formula and line.get('report_id') in report_formula_by_id:
                formula = report_formula_by_id[line['report_id']]
            if not formula and row_key.startswith('account-type-'):
                account_type = self.env['account.account.type'].browse(int(row_key.rsplit('-', 1)[-1]))
                if account_type.exists():
                    line['account_type'] = account_type.type
            account_type_domains = {
                'asset_receivable': "[('account_id.account_type', '=', 'asset_receivable'), ('account_id.non_trade', '=', False)]",
                'asset_current': "['|', ('account_id.account_type', '=', 'asset_current'), '&', ('account_id.account_type', '=', 'asset_receivable'), ('account_id.non_trade', '=', True)]",
                'liability_current': "['|', ('account_id.account_type', '=', 'liability_current'), '&', ('account_id.account_type', '=', 'liability_payable'), ('account_id.non_trade', '=', True)]",
                'liability_payable': "[('account_id.account_type', '=', 'liability_payable'), ('account_id.non_trade', '=', False)]",
            }
            if row_type != 'account' and line.get('account_type') in account_type_domains:
                formula = account_type_domains[line['account_type']]
            engine = 'Aggregate Other Formulas' if formula and row_type in {'report', 'group', 'total'} else 'Odoo Domain'
            subformula = None
            if not formula:
                account_type = line.get('account_type')
                if account_type:
                    formula = "[('account_id.account_type', '=', '%s')]" % account_type
                    if account_type in {'liability_current', 'liability_credit_card', 'liability_payable',
                                        'liability_non_current', 'equity'}:
                        subformula = '-sum'
                    else:
                        subformula = 'sum'
                elif line.get('account_id'):
                    formula = "[('account_id', '=', %s)]" % line['account_id']
                    subformula = 'sum'
                else:
                    formula = '0.0'
                    engine = 'Odoo Domain'
            line['formula_info'] = {
                'engine': engine,
                'label': 'balance',
                'formula': formula,
                'subformula': subformula,
                'value': line.get('balance', 0.0),
            }
            return line

        def account_lines_for_types(types, context):
            accounts = self.env['account.account'].search([
                ('account_type', 'in', list(types)),
                ('company_ids', 'child_of', company.id),
            ])
            return self.with_context(context)._compute_account_balance(accounts)

        def profit_and_loss_lines(context):
            profit_report = self.env.ref('accounting_pdf_reports.account_financial_report_profitandloss0')
            profit_data = {
                'account_report_id': (profit_report.id, profit_report.display_name),
                'used_context': context,
                'enable_filter': False,
                'debit_credit': False,
            }
            direct_report_ids = set(profit_report.children_ids.ids)
            report_lines = self.get_account_lines(profit_data)
            top_lines = [row for row in report_lines if row.get('report_id') in direct_report_ids]
            detail_lines = [row for row in report_lines if row.get('account_id')]
            return sum(row['balance'] for row in top_lines), detail_lines

        all_lines = self.get_account_lines(data)
        lines = []
        expanded_group_keys = []
        index = 0
        while index < len(all_lines):
            line = all_lines[index]
            if line.get('report_id') in (report.id, hidden_wrapper.id):
                index += 1
                continue
            section = self.env['account.financial.report'].browse(line['report_id']) if line.get('report_id') else False
            equity_report = self.env.ref('accounting_pdf_reports.account_financial_report_equity0')
            parent = section.parent_id if section else self.env['account.financial.report']
            while parent:
                if parent == hidden_wrapper:
                    line['level'] = max(line['level'] - 1, 1)
                    break
                parent = parent.parent_id
            if not section or (section.type != 'account_type' and section != equity_report):
                if line.get('account_id'):
                    line['row_key'] = f"account-{line['account_id']}"
                lines.append(line)
                index += 1
                continue

            account_lines = []
            next_index = index + 1
            while next_index < len(all_lines) and all_lines[next_index].get('type') == 'account':
                account_lines.append(all_lines[next_index])
                next_index += 1
            categories = []
            type_order = {
                'asset_cash': 10, 'asset_receivable': 20, 'asset_current': 30,
                'asset_prepayments': 40, 'asset_fixed': 50, 'asset_non_current': 60,
                'liability_current': 70, 'liability_credit_card': 80,
                'liability_payable': 90, 'liability_non_current': 100,
            }
            ordered_types = section.account_type_ids.sorted(
                key=lambda account_type: (type_order.get(account_type.type, 1000), account_type.id)
            )
            for account_type in ordered_types:
                category_accounts = [account for account in account_lines
                                     if account.get('account_type') == account_type.type
                                     and (account_type.type != 'asset_receivable' or not account.get('non_trade'))
                                     and (account_type.type != 'liability_payable' or not account.get('non_trade'))]
                if account_type.type == 'asset_current':
                    category_accounts.extend(
                        account for account in account_lines
                        if account.get('account_type') == 'asset_receivable' and account.get('non_trade')
                    )
                elif account_type.type == 'liability_current':
                    category_accounts.extend(
                        account for account in account_lines
                        if account.get('account_type') == 'liability_payable' and account.get('non_trade')
                    )
                category_name = {
                    'asset_cash': _('Bank and Cash Accounts'),
                    'asset_receivable': _('Receivables'),
                    'asset_current': _('Current Assets'),
                    'liability_payable': _('Payables'),
                    'liability_current': _('Current Liabilities'),
                }.get(account_type.type, account_type.name)
                categories.append((account_type, category_accounts, category_name))

            if section.id == self.env.ref('accounting_pdf_reports.account_financial_report_assets0').id:
                line['name'] = _('ASSETS')
                line['show_amount'] = False
                lines.append(line)
                current = [(record, accounts, name) for record, accounts, name in categories
                           if record.type in current_asset_types]
                current_key = f"asset-current-{section.id}"
                lines.append(amount_row(_('Current Assets'), 'group', current_key,
                                        line['level'] + 1, [], show_amount=False))
                expanded_group_keys.append(current_key)
                for record, accounts, name in current:
                    key = f"account-type-{section.id}-{record.id}"
                    lines.append(amount_row(name, 'category', key, line['level'] + 2,
                                            accounts,
                                            extra_account_ids=account_ids_for_types({record.type})))
                    for account in accounts:
                        lines.append({**account, 'row_key': f"account-{account['account_id']}",
                                      'level': line['level'] + 3})
                lines.append(amount_row(_('Total Current Assets'), 'total', f"asset-total-current-{section.id}",
                                        line['level'] + 1,
                                        [account for _, accounts, _ in current for account in accounts],
                                        extra_account_ids=account_ids_for_types(
                                            {record.type for record, _, _ in current})))
                for record, accounts, name in categories:
                    if record.type not in fixed_asset_types:
                        continue
                    lines.append(amount_row(name, 'category', f"account-type-{section.id}-{record.id}",
                                            line['level'] + 1, accounts,
                                            extra_account_ids=account_ids_for_types({record.type})))
                    for account in accounts:
                        lines.append({**account, 'row_key': f"account-{account['account_id']}",
                                      'level': line['level'] + 2})
                lines.append(amount_row(_('Total ASSETS'), 'total', f"asset-total-{section.id}",
                                        line['level'], account_lines,
                                        extra_account_ids=account_ids_for_types(
                                            {record.type for record, _, _ in categories})))
            elif section.id == self.env.ref('accounting_pdf_reports.account_financial_report_liability0').id:
                line['name'] = _('LIABILITIES')
                line['show_amount'] = False
                lines.append(line)
                current = [(record, accounts, name) for record, accounts, name in categories
                           if record.type in current_liability_types]
                current_key = f"liability-current-{section.id}"
                lines.append(amount_row(_('Current Liabilities'), 'group', current_key,
                                        line['level'] + 1, [], show_amount=False))
                expanded_group_keys.append(current_key)
                for record, accounts, name in current:
                    key = f"account-type-{section.id}-{record.id}"
                    lines.append(amount_row(name, 'category', key, line['level'] + 2,
                                            accounts,
                                            extra_account_ids=account_ids_for_types({record.type})))
                    for account in accounts:
                        lines.append({**account, 'row_key': f"account-{account['account_id']}",
                                      'level': line['level'] + 3})
                lines.append(amount_row(_('Total Current Liabilities'), 'total',
                                        f"liability-total-current-{section.id}", line['level'] + 1,
                                        [account for _, accounts, _ in current for account in accounts],
                                        extra_account_ids=account_ids_for_types(
                                            {record.type for record, _, _ in current})))
                for record, accounts, name in categories:
                    if record.type not in {'liability_non_current'}:
                        continue
                    lines.append(amount_row(name, 'category', f"account-type-{section.id}-{record.id}",
                                            line['level'] + 1, accounts,
                                            extra_account_ids=account_ids_for_types({record.type})))
                    for account in accounts:
                        lines.append({**account, 'row_key': f"account-{account['account_id']}",
                                      'level': line['level'] + 2})
                lines.append(amount_row(_('Total LIABILITIES'), 'total', f"liability-total-{section.id}",
                                        line['level'], account_lines,
                                        extra_account_ids=account_ids_for_types(
                                            {record.type for record, _, _ in categories})))
            elif section.id == self.env.ref('accounting_pdf_reports.account_financial_report_equity0').id:
                line['name'] = _('EQUITY (& EARNINGS)')
                line['show_amount'] = False
                lines.append(line)

                equity_accounts = account_lines_for_types({'equity'}, context)
                equity_lines = []
                for account_id, value in equity_accounts.items():
                    account = self.env['account.account'].browse(account_id)
                    equity_lines.append({
                        'name': ' '.join(part for part in (account.code, account.name) if part),
                        'account_id': account.id,
                        'account_type': account.account_type,
                        'debit': value['debit'],
                        'credit': value['credit'],
                        'balance': -value['balance'],
                    })
                lines.append(amount_row(_('Capital'), 'category', f"equity-accounts-{section.id}",
                                        line['level'] + 1, equity_lines,
                                        extra_account_ids=account_ids_for_types({'equity'})))
                for account in equity_lines:
                    lines.append({**account, 'row_key': f"account-{account['account_id']}",
                                  'level': line['level'] + 2})

                earnings_key = f"earnings-{section.id}"
                lines.append(amount_row(_('Earnings'), 'group', earnings_key,
                                        line['level'] + 1, [], show_amount=False))
                expanded_group_keys.append(earnings_key)
                year_dates = company.compute_fiscalyear_dates(fields.Date.to_date(date_to))
                fiscalyear_start = year_dates['date_from']
                current_context = dict(context, date_from=fiscalyear_start.isoformat(),
                                       date_to=date_to, strict_range=True)
                current_earnings, current_pnl_accounts = profit_and_loss_lines(current_context)
                profit_loss_types = {
                    'income', 'income_other', 'expense', 'expense_other',
                    'expense_depreciation', 'expense_direct_cost',
                }
                current_earning_line = {
                    'name': _('Current Year Unallocated Earnings'), 'type': 'category',
                    'row_key': f"current-year-earnings-{section.id}",
                    'level': line['level'] + 2, 'debit': sum(row.get('debit', 0.0) for row in current_pnl_accounts),
                    'credit': sum(row.get('credit', 0.0) for row in current_pnl_accounts),
                    'balance': current_earnings,
                    'account_ids': account_ids_for_types(profit_loss_types),
                    'detail_date_from': fiscalyear_start.isoformat(),
                    'detail_date_to': date_to,
                }
                lines.append(current_earning_line)

                prior_earnings = 0.0
                prior_accounts = []
                prior_end = fields.Date.to_date(fiscalyear_start) - relativedelta(days=1)
                if prior_end:
                    prior_context = dict(context, date_from=False, date_to=prior_end.isoformat(),
                                         strict_range=False)
                    prior_result, prior_pnl_accounts = profit_and_loss_lines(prior_context)
                    prior_earnings += prior_result
                    prior_accounts.extend(prior_pnl_accounts)
                unaffected = account_lines_for_types({'equity_unaffected'}, context)
                for account_id, value in unaffected.items():
                    account = self.env['account.account'].browse(account_id)
                    prior_accounts.append({
                        'account_id': account.id, 'debit': value['debit'],
                        'credit': value['credit'], 'balance': -value['balance'],
                    })
                    prior_earnings += -value['balance']
                prior_row = {
                    'name': _('Previous Years Earnings'), 'type': 'category',
                    'row_key': f"previous-years-earnings-{section.id}",
                    'level': line['level'] + 2,
                    'debit': sum(row.get('debit', 0.0) for row in prior_accounts),
                    'credit': sum(row.get('credit', 0.0) for row in prior_accounts),
                    'balance': prior_earnings,
                    'account_ids': account_ids_for_types(profit_loss_types | {'equity_unaffected'}),
                    'detail_date_from': False,
                    'detail_date_to': prior_end.isoformat(),
                }
                lines.append(prior_row)
                earnings_total = amount_row(_('Total Earnings'), 'total',
                                            f"earnings-total-{section.id}", line['level'] + 1,
                                            [current_earning_line, prior_row])
                lines.append(earnings_total)
                lines.append(amount_row(_('Total EQUITY (& EARNINGS)'), 'total',
                                        f"equity-total-{section.id}", line['level'],
                                        equity_lines + [current_earning_line, prior_row]))
                total_liabilities = next(
                    row for row in lines if row.get('row_key') ==
                    f"liability-total-{self.env.ref('accounting_pdf_reports.account_financial_report_liability0').id}"
                )
                total_equity = lines[-1]
                lines.append(amount_row(_('LIABILITIES + EQUITY'), 'total',
                                        f"liabilities-equity-total-{section.id}", line['level'],
                                        [total_liabilities, total_equity]))

                next_index = index + 1
                while next_index < len(all_lines) and all_lines[next_index]['level'] > line['level']:
                    next_index += 1
                index = next_index
                continue
            else:
                lines.append(line)
                for record, accounts, name in categories:
                    key = f"account-type-{section.id}-{record.id}"
                    lines.append(amount_row(name, 'category', key, line['level'] + 1,
                                            accounts,
                                            extra_account_ids=account_ids_for_types({record.type})))
                    for account in accounts:
                        lines.append({**account, 'row_key': f"account-{account['account_id']}",
                                      'level': line['level'] + 2})
            index = next_index
        drafts_domain = [
            ('state', '=', 'draft'), ('company_id', 'child_of', company.id),
            ('journal_id', 'in', journals.ids),
        ]
        if date_from:
            drafts_domain.append(('date', '>=', date_from))
        if date_to:
            drafts_domain.append(('date', '<=', date_to))
        return {
            'name': report.display_name,
            'lines': [add_formula_info(line) for line in lines],
            'expanded_report_ids': [line['report_id'] for line in lines if line.get('type') == 'report'],
            'expanded_group_keys': expanded_group_keys,
            'date_from': date_from or False,
            'date_to': date_to,
            'currency_id': company.currency_id.id,
            'company_id': company.id,
            'company_name': company.display_name,
            'draft_count': self.env['account.move'].search_count(drafts_domain),
            'journal_ids': journals.ids,
            'journals': [{'id': journal.id, 'name': journal.display_name} for journal in journals],
            'comparison_context': data.get('comparison_context') or False,
        }

    @api.model
    def _get_report_values(self, docids, data=None):
        if (not data.get('form') or not self.env.context.get('active_model')
                or self.env.context.get('active_id') is None):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        report_data = docs._get_interactive_report_data(data['form'])
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'report_lines': report_data['lines'],
        }
