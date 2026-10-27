import time
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


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
    def get_interactive_data(self, report_id, date_from, date_to, target_move='posted',
                             journal_ids=None, comparison=False, debit_credit=False):
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
        if comparison:
            start = fields.Date.to_date(date_from) if date_from else False
            end = fields.Date.to_date(date_to) if date_to else fields.Date.context_today(self)
            if start:
                if start.month == 1 and start.day == 1:
                    comparison_start = start - relativedelta(years=1)
                    comparison_end = end - relativedelta(years=1)
                else:
                    days = (end - start).days + 1
                    comparison_start = start - relativedelta(days=days)
                    comparison_end = start - relativedelta(days=1)
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

        def amount_row(name, row_type, row_key, level, accounts, show_amount=True):
            values = {
                field: sum(account.get(field, 0.0) for account in accounts)
                for field in ('debit', 'credit', 'balance', 'balance_cmp')
            }
            return {
                'name': name, 'type': row_type, 'row_key': row_key, 'level': level,
                'show_amount': show_amount, **values,
            }

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
            parent = section.parent_id if section else self.env['account.financial.report']
            while parent:
                if parent == hidden_wrapper:
                    line['level'] = max(line['level'] - 1, 1)
                    break
                parent = parent.parent_id
            if not section or section.type != 'account_type':
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
            for account_type in section.account_type_ids.sorted('id'):
                category_accounts = [account for account in account_lines
                                     if account.get('account_type') == account_type.type]
                category_name = {
                    'asset_cash': _('Bank and Cash Accounts'),
                    'asset_receivable': _('Receivables'),
                }.get(account_type.type, account_type.name)
                categories.append((account_type, category_accounts, category_name))

            if section.id == self.env.ref('accounting_pdf_reports.account_financial_report_assets0').id:
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
                                            accounts))
                    for account in accounts:
                        lines.append({**account, 'row_key': f"account-{account['account_id']}",
                                      'level': line['level'] + 3})
                lines.append(amount_row(_('Total Current Assets'), 'total', f"asset-total-current-{section.id}",
                                        line['level'] + 1,
                                        [account for _, accounts, _ in current for account in accounts]))
                for record, accounts, name in categories:
                    if record.type not in fixed_asset_types:
                        continue
                    lines.append(amount_row(name, 'category', f"account-type-{section.id}-{record.id}",
                                            line['level'] + 1, accounts))
                    for account in accounts:
                        lines.append({**account, 'row_key': f"account-{account['account_id']}",
                                      'level': line['level'] + 2})
                lines.append(amount_row(_('Total Assets'), 'total', f"asset-total-{section.id}",
                                        line['level'], account_lines))
            elif section.id == self.env.ref('accounting_pdf_reports.account_financial_report_liability0').id:
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
                                            accounts))
                    for account in accounts:
                        lines.append({**account, 'row_key': f"account-{account['account_id']}",
                                      'level': line['level'] + 3})
                lines.append(amount_row(_('Total Current Liabilities'), 'total',
                                        f"liability-total-current-{section.id}", line['level'] + 1,
                                        [account for _, accounts, _ in current for account in accounts]))
                for record, accounts, name in categories:
                    if record.type not in {'liability_non_current'}:
                        continue
                    lines.append(amount_row(name, 'category', f"account-type-{section.id}-{record.id}",
                                            line['level'] + 1, accounts))
                    for account in accounts:
                        lines.append({**account, 'row_key': f"account-{account['account_id']}",
                                      'level': line['level'] + 2})
                lines.append(amount_row(_('Total Liabilities'), 'total', f"liability-total-{section.id}",
                                        line['level'], account_lines))
            else:
                lines.append(line)
                for record, accounts, name in categories:
                    key = f"account-type-{section.id}-{record.id}"
                    lines.append(amount_row(name, 'category', key, line['level'] + 1,
                                            accounts))
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
            'lines': lines,
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
        }

    @api.model
    def _get_report_values(self, docids, data=None):
        if (not data.get('form') or not self.env.context.get('active_model')
                or self.env.context.get('active_id') is None):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        report_lines = self.get_account_lines(data.get('form'))
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_account_lines': report_lines,
        }
