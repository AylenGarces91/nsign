# -*- coding: utf-8 -*-
import logging

from odoo import models, _

_logger = logging.getLogger(__name__)

class account_financial_html_report_custom(models.Model):
    _inherit = 'account.financial.html.report'

    # group_account_type_filter = fields.Boolean('Group by account type')

    def _get_options(self, options):
        if (options != False and options.get("group_company", False)):
            self.filter_group_company = options['group_company']
        else:
            self.filter_group_company = False
        to_return = super(account_financial_html_report_custom, self)._get_options(options)
        return to_return


class AccountReportCustom(models.AbstractModel):
    _inherit = 'account.report'

    filter_group_company = None
