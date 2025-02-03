# -*- coding: utf-8 -*-

import json

from odoo import models, _, fields
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.misc import format_date, get_lang

from datetime import timedelta
from collections import defaultdict


class ResPartner(models.Model):
    _inherit = 'res.partner'

    hide_peppol_fields = fields.Boolean()
    is_coa_installed = fields.Boolean()


class PartnerLedgerCustomHandler(models.AbstractModel):
    _inherit = 'account.partner.ledger.report.handler'

    def _get_report_line_move_line(self, options, aml_query_result, partner_line_id, init_bal_by_col_group,
                                   level_shift=0):
        if aml_query_result['payment_id']:
            caret_type = 'account.payment'
        else:
            caret_type = 'account.move.line'

        columns = []
        report = self.env['account.report'].browse(options['report_id'])
        for column in options['columns']:
            col_expr_label = column['expression_label']
            if col_expr_label == 'ref':
                col_value = report._format_aml_name(aml_query_result['name'], aml_query_result['ref'],
                                                    aml_query_result['move_name'])
            else:
                account_lot_ids = self.env['account.move.line'].search([('id', '=', aml_query_result['id'])], limit=1)
                aml_query_result['project_id'] = account_lot_ids.move_id.project_id.name  if account_lot_ids.move_id.project_id else ''
                aml_query_result['contract_id'] = account_lot_ids.move_id.contract_id.name  if account_lot_ids.move_id.contract_id else ''
                col_value = aml_query_result[col_expr_label] if column['column_group_key'] == aml_query_result[
                    'column_group_key'] else None

            if col_value is None:
                columns.append({})
            else:
                col_class = 'number'

                if col_expr_label == 'date_maturity':
                    formatted_value = format_date(self.env, fields.Date.from_string(col_value))
                    col_class = 'date'
                elif col_expr_label == 'amount_currency':
                    currency = self.env['res.currency'].browse(aml_query_result['currency_id'])
                    formatted_value = report.format_value(options, col_value, currency=currency,
                                                          figure_type=column['figure_type'])
                elif col_expr_label == 'balance':
                    col_value += init_bal_by_col_group[column['column_group_key']]
                    formatted_value = report.format_value(options, col_value, figure_type=column['figure_type'],
                                                          blank_if_zero=column['blank_if_zero'])
                else:
                    if col_expr_label == 'ref':
                        col_class = 'o_account_report_line_ellipsis'
                    elif col_expr_label not in ('debit', 'credit'):
                        col_class = ''
                    formatted_value = report.format_value(options, col_value, figure_type=column['figure_type'])

                columns.append({
                    'name': formatted_value,
                    'no_format': col_value,
                    'class': col_class,
                })

        return {
            'id': report._get_generic_line_id('account.move.line', aml_query_result['id'],
                                              parent_line_id=partner_line_id, markup=aml_query_result['partial_id']),

            'parent_id': partner_line_id,
            'name': self._format_aml_name(aml_query_result['name'], aml_query_result['ref'], aml_query_result['move_name']),
            # 'class': 'text-muted' if aml_query_result['key'] == 'indirectly_linked_aml' else 'text',
            # do not format as date to prevent text centering
            'columns': columns,
            'caret_options': caret_type,
            'level': 4 + level_shift,
        }