# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class analytic_report_custom(models.AbstractModel):
    _inherit = 'account.analytic.report'
    _name = 'account.analytic.report.custom'
    _description = 'Account Analytic Report Custom'

    filter_analytic = None
    filter_group_company = False
    filter_partner = True

    def _get_columns_name(self, options):
        return [{'name': _('Partner')},
                {'name': _('Reference')},
                {'name': _('Analytic account')},
                {'name': _('Balance'), 'class': 'number'}]

    @api.model
    def _get_report_name(self):
        return _('Analytic Report Custom')

    def _generate_analytic_account_lines(self, analytic_accounts, parent_id=False):
        lines = []
        for account in analytic_accounts:
            # filter all analytics accounts if the account is related to a company
            if account.partner_id and account.partner_id.is_company:
                lines.append({
                    'id': 'analytic_account_%s' % account.id,
                    'name': account.partner_id.display_name,
                    'columns': [{'name': account.code},
                                {'name': account.name},
                                {'name': self.format_value(account.balance)}],
                    'level': 4,  # todo check redesign financial reports, should be level + 1 but doesn't look good
                    'unfoldable': False,
                    'caret_options': 'account.analytic.account',
                    'parent_id': parent_id,  # to make these fold when the original parent gets folded
                })

        return lines

    @api.model
    def _get_lines(self, options, line_id=None):
        lines = []

        date_from = options['date']['date_from']
        date_to = options['date']['date_to']

        # context is set because it's used for the debit, credit and balance computed fields
        AccountAnalyticAccount = self.env['account.analytic.account'].with_context(from_date=date_from,
                                                                                   to_date=date_to)
        # The options refer to analytic entries. So first determine
        # the subset of analytic categories we have to search in.
        analytic_entries_domain = [('date', '>=', date_from),
                                   ('date', '<=', date_to),
                                   ('account_id.partner_id', '!=', False)]
        analytic_account_domain = []

        if options.get('partner_ids'):
            analytic_partner_ids = [int(id) for id in options['partner_ids']]
            analytic_entries_domain += [('account_id.partner_id.id', 'in', analytic_partner_ids)]
            analytic_account_domain += [('partner_id.id', 'in', analytic_partner_ids)]

        if options.get('partner_categories'):
            analytic_partner_categories = [int(id) for id in options['partner_categories']]
            analytic_entries_domain += [('account_id.partner_id.category_id.id', 'in', analytic_partner_categories)]
            analytic_account_domain += [('partner_id.category_id.id', 'in', analytic_partner_categories)]


        if options.get('multi_company'):
            company_ids = [company['id'] for company in options['multi_company'] if company['selected']]
            if company_ids:
                analytic_entries_domain += [('company_id', 'in', company_ids)]
                analytic_account_domain += ['|', ('company_id', 'in', company_ids), ('company_id', '=', False)]
                AccountAnalyticAccount = AccountAnalyticAccount.with_context(company_ids=company_ids)

        if options['group_company']:
            return self.company_flow(AccountAnalyticAccount, analytic_account_domain,
                       analytic_entries_domain, lines, options)
        elif options['hierarchy']:
            return self.hierarchy_flow(AccountAnalyticAccount, analytic_account_domain,
                                        analytic_entries_domain, line_id, lines, options)
        else:
            return self._generate_analytic_account_lines(AccountAnalyticAccount.search(analytic_account_domain))

    def _get_balance_for_company(self, company, analytic_line_domain):
        analytic_line_domain_for_group = [('account_id.partner_id.id', '=', company.id)]
        analytic_line_domain_for_group += analytic_line_domain
        currency_obj = self.env['res.currency']
        user_currency = self.env.company.currency_id

        analytic_lines = self.env['account.analytic.line'].read_group(analytic_line_domain_for_group, ['amount', 'currency_id'], ['currency_id'])
        balance = sum([currency_obj.browse(row['currency_id'][0])._convert(
            row['amount'], user_currency, self.env.company, fields.Date.today()) for row in analytic_lines])
        return balance

    def _generate_company_group_line(self, company, analytic_line_domain, unfolded=False):
        balance = self._get_balance_for_company(company, analytic_line_domain)
        return {
            'id': company.id,
            'name': company.display_name,
            'level': 1,
            'parent_id': False,
            'columns': [{'name': ''},
                        {'name': ''},
                        {'name': self.format_value(balance)}],
            'unfoldable': True,
            'unfolded': unfolded,
        }

    def company_flow(self, AccountAnalyticAccount, analytic_account_domain,
                       analytic_entries_domain, lines, options):

        analytic_accounts = AccountAnalyticAccount.search(analytic_account_domain)
        companies = analytic_accounts.mapped('partner_id')

        for company in companies:
            company_domain = [('partner_id', '=', company.id)]
            company_domain += analytic_account_domain
            company_analytic_accounts = AccountAnalyticAccount.search(company_domain)
            lines.append(self._generate_company_group_line(company, analytic_entries_domain, unfolded=True))
            lines += self._generate_analytic_account_lines(company_analytic_accounts, company.id)

        return lines

    def hierarchy_flow(self, AccountAnalyticAccount, analytic_account_domain,
                       analytic_entries_domain, line_id, lines, options):
        AccountAnalyticGroup = self.env['account.analytic.group']
        # display all groups that have accounts
        analytic_accounts = AccountAnalyticAccount.search(analytic_account_domain)
        analytic_groups = analytic_accounts.mapped('group_id')
        # also include the parent analytic groups, even if they didn't have a child analytic line
        if analytic_groups:
            analytic_groups = AccountAnalyticGroup.search([('id', 'parent_of', analytic_groups.ids)])
        domain = [('id', 'in', analytic_groups.ids)]
        if line_id:
            parent_group = AccountAnalyticGroup if line_id == self.DUMMY_GROUP_ID else AccountAnalyticGroup.browse(
                int(line_id))
            domain += [('parent_id', '=', parent_group.id)]

            # the engine replaces line_id with what is returned so
            # first re-render the line that was just clicked
            lines.append(self._generate_analytic_group_line(parent_group, analytic_entries_domain, unfolded=True))

            # append analytic accounts part of this group, taking into account the selected options
            analytic_account_domain += [('group_id', '=', parent_group.id)]

            analytic_accounts = AccountAnalyticAccount.search(analytic_account_domain)
            lines += self._generate_analytic_account_lines(analytic_accounts,
                                                           parent_group.id if parent_group else self.DUMMY_GROUP_ID)
        else:
            domain += [('parent_id', '=', False)]
        # append children groups unless the dummy group has been clicked, it has no children
        if line_id != self.DUMMY_GROUP_ID:
            for group in AccountAnalyticGroup.search(domain):
                if group.id in options.get('unfolded_lines') or options.get('unfold_all'):
                    lines += self._get_lines(options, line_id=str(group.id))
                else:
                    lines.append(self._generate_analytic_group_line(group, analytic_entries_domain))
        # finally append a 'dummy' group which contains the accounts that do not have an analytic group
        if not line_id and any(not account.group_id for account in analytic_accounts):
            if self.DUMMY_GROUP_ID in options.get('unfolded_lines'):
                lines += self._get_lines(options, line_id=self.DUMMY_GROUP_ID)
            else:
                lines.append(self._generate_analytic_group_line(AccountAnalyticGroup, analytic_entries_domain))
        return lines
