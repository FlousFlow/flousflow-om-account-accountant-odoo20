from collections import defaultdict

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, ValidationError


ACCOUNT_SCOPES = {
    'receivable': ('asset_receivable', False),
    'non_trade_receivable': ('asset_current', True),
    'payable': ('liability_payable', False),
    'non_trade_payable': ('liability_current', True),
}
REPORT_GROUPS = (
    'account.group_account_readonly',
    'account.group_account_invoice',
    'account.group_account_user',
    'account.group_account_manager',
)


class ReportCustomerStatement(models.AbstractModel):
    _name = 'report.accounting_pdf_reports.customer_statement_data'
    _description = 'Interactive Customer and Vendor Statement Data'

    @api.model
    def get_interactive_data(self, period_type='month', period_anchor=None,
                             custom_date_from=None, custom_date_to=None,
                             account_scopes=None, partner_ids=None, partner_tag_ids=None,
                             target_move='posted'):
        self._check_report_access()
        if target_move not in ('posted', 'draft', 'all'):
            raise ValidationError(_('Choose a valid journal entry state.'))
        account_scopes = account_scopes or ['receivable', 'payable']
        if not isinstance(account_scopes, list) or not account_scopes or any(
                scope not in ACCOUNT_SCOPES for scope in account_scopes):
            raise ValidationError(_('Choose at least one valid account scope.'))
        try:
            date_from, date_to = self.env['report.accounting_pdf_reports.report_general_ledger']._get_interactive_period_dates(
                period_type, period_anchor, custom_date_from, custom_date_to
            )
        except (TypeError, ValueError):
            raise ValidationError(_('Choose a valid statement period.'))

        company = self.env.company
        companies = self.env['res.company'].search([('id', 'child_of', company.id)])
        Account = self.env['account.account']
        account_ids = set()
        for scope in account_scopes:
            account_type, requires_reconcile = ACCOUNT_SCOPES[scope]
            domain = [
                ('company_ids', 'in', companies.ids),
                ('account_type', '=', account_type),
                ('active', '=', True),
            ]
            if requires_reconcile:
                domain.append(('reconcile', '=', True))
            account_ids.update(Account.search(domain).ids)

        partner_ids = self._validated_ids('res.partner', partner_ids, _('partner'))
        if partner_ids:
            partner_ids = self.env['res.partner'].browse(partner_ids).mapped('commercial_partner_id').ids
        partner_tag_ids = self._validated_ids('res.partner.category', partner_tag_ids, _('partner tag'))
        domain = [
            ('company_id', 'in', companies.ids),
            ('account_id', 'in', list(account_ids)),
            ('partner_id', '!=', False),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('display_type', 'not in', ('line_section', 'line_note')),
        ]
        if target_move in ('posted', 'draft'):
            domain.append(('parent_state', '=', target_move))
        else:
            domain.append(('parent_state', 'in', ('posted', 'draft')))
        if partner_ids:
            domain.append(('partner_id.commercial_partner_id', 'in', partner_ids))
        if partner_tag_ids:
            domain.append(('partner_id.commercial_partner_id.category_id', 'in', partner_tag_ids))

        move_lines = self.env['account.move.line'].search(domain, order='date, move_id, id')
        if len(move_lines) > 10000:
            raise ValidationError(_(
                'This statement contains more than 10,000 journal items. Narrow the period or select specific partners.'
            ))

        grouped = defaultdict(list)
        partner_totals = defaultdict(float)
        for line in move_lines:
            partner = line.partner_id.commercial_partner_id
            amount = line.debit - line.credit
            partner_totals[partner.id] += amount
            grouped[partner.id].append({
                'id': line.id,
                'move_id': line.move_id.id,
                'date': fields.Date.to_string(line.date),
                'date_maturity': fields.Date.to_string(line.date_maturity) if line.date_maturity else False,
                'label': line.name or line.move_id.ref or line.move_id.name,
                'reference': line.move_id.ref or line.move_id.name,
                'amount': amount,
                'amount_currency': line.amount_currency,
                'currency_id': line.currency_id.id,
                'currency_name': line.currency_id.name,
                'currency_symbol': line.currency_id.symbol,
            })

        partners = self.env['res.partner'].browse(list(grouped))
        partners = partners.sorted(lambda partner: (partner.name or '').casefold())
        return {
            'date_from': date_from,
            'date_to': date_to,
            'period_type': period_type,
            'target_move': target_move,
            'company_id': company.id,
            'company_name': company.name,
            'currency_id': company.currency_id.id,
            'currency_name': company.currency_id.name,
            'currency_symbol': company.currency_id.symbol,
            'partners': [{
                'id': partner.id,
                'name': partner.display_name,
                'amount': partner_totals[partner.id],
                'lines': grouped[partner.id],
            } for partner in partners],
            'line_count': len(move_lines),
        }

    @api.model
    def _validated_ids(self, model_name, values, label):
        if not values:
            return []
        if not isinstance(values, list):
            raise ValidationError(_('Invalid %(label)s selection.', label=label))
        try:
            ids = list({int(value) for value in values})
        except (TypeError, ValueError):
            raise ValidationError(_('Invalid %(label)s selection.', label=label))
        records = self.env[model_name].search([('id', 'in', ids)])
        if len(records) != len(ids):
            raise ValidationError(_('One or more selected %(label)s are unavailable.', label=label))
        return records.ids

    @api.model
    def _check_report_access(self):
        if not any(self.env.user.has_group(group) for group in REPORT_GROUPS):
            raise AccessError(_('You are not allowed to view Customer Statements.'))

    @api.model
    def search_partners(self, search_term=''):
        self._check_report_access()
        companies = self.env['res.company'].search([('id', 'child_of', self.env.company.id)])
        domain = [('parent_id', '=', False), ('company_id', 'in', [False] + companies.ids)]
        if search_term:
            domain.append(('name', 'ilike', search_term.strip()))
        partners = self.env['res.partner'].search(domain, order='name', limit=40)
        return [{'id': partner.id, 'name': partner.display_name} for partner in partners]

    @api.model
    def get_partner_tags(self):
        self._check_report_access()
        tags = self.env['res.partner.category'].search([], order='name', limit=200)
        return [{'id': tag.id, 'name': tag.name} for tag in tags]
