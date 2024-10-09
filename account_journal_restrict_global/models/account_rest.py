from odoo import fields, models, api

import logging
import requests

_logger = logging.getLogger(__name__)


def print_log(*s):
    print(s)
    _logger.info(f"#######################{s}")


class Journal(models.Model):
    _inherit = 'account.journal'
    is_show = fields.Boolean()

    # @api.model
    # def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
    #     print('yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy')
    #
    #     if self.env.user.has_group(
    #             'dvit_account_journal_restrict.journal_restrict_group') and self.env.user.journal_ids:
    #         domain = [('id', 'in', self.env.user.journal_ids.ids)]
    #         print('xxxxxxxxxxxxxxxxxxxxxxxxxxx', domain)
    #     return super()._search(domain=domain, offset=offset, limit=limit, order=order,
    #                            access_rights_uid=access_rights_uid)

    # @api.model
    # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
    #     print('rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr')
    #     if self.env.user.has_group(
    #             'dvit_account_journal_restrict.journal_restrict_group') and self.env.user.journal_ids:
    #         domain = [('id', 'in', self.env.user.journal_ids.ids)]
    #
    #     return super(Journal, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit,
    #                                             order=order)


class Move(models.Model):
    _inherit = 'account.move'
    is_show = fields.Boolean()

    # @api.model
    # def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
    #     print('yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy')
    #
    #     if self.env.user.has_group(
    #             'dvit_account_journal_restrict.journal_restrict_group') and self.env.user.journal_ids:
    #         domain = [('journal_id', 'in', self.env.user.journal_ids.ids)]
    #         print('xxxxxxxxxxxxxxxxxxxxxxxxxxx', domain)
    #     return super()._search(domain=domain, offset=offset, limit=limit, order=order, access_rights_uid=access_rights_uid)

    # @api.onchange('journal_id')
    # def _onchange_journal_id(self):
    #     if self.env.user.journal_ids and self.env.user.journal_ids and self.env.user.has_group(
    #             'dvit_account_journal_restrict.journal_restrict_group'):
    #         domain = []
    #         domain.append(('id', '=', self.env.user.journal_ids.ids))
    #         if self.move_type in ('out_invoice', 'out_refund'):
    #             domain.append(('type', '=', 'sale'))
    #         if self.move_type in ('in_invoice', 'in_refund'):
    #             domain.append(('type', '=', 'purchase'))
    #
    #         return {
    #             'domain': {'journal_id': domain}}

    # @api.model
    # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
    #     print('tttttttttttttttttttttttt')
    #     if self.env.user.has_group(
    #             'dvit_account_journal_restrict.journal_restrict_group') and self.env.user.journal_ids:
    #         domain = [('journal_id', 'in', self.env.user.journal_ids.ids)]
    #
    #     return super(Move, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit,
    #                                          order=order)


class Payment(models.Model):
    _inherit = 'account.payment'
    is_show = fields.Boolean()

    # @api.model
    # def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
    #     print('yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy')
    #
    #     if self.env.user.has_group(
    #             'dvit_account_journal_restrict.journal_restrict_group') and self.env.user.journal_ids:
    #         domain = [('journal_id', 'in', self.env.user.journal_ids.ids)]
    #         print('xxxxxxxxxxxxxxxxxxxxxxxxxxx', domain)
    #     return super()._search(domain=domain, offset=offset, limit=limit, order=order,
    #                            access_rights_uid=access_rights_uid)

    # @api.onchange('journal_id')
    # def _onchange_journal_id(self):
    #     if self.env.user.journal_ids and self.env.user.journal_ids and self.env.user.has_group(
    #             'dvit_account_journal_restrict.journal_restrict_group'):
    #         domain = []
    #         domain.append(('id', '=', self.env.user.journal_ids.ids))
    #         domain.append(('type', 'in', ('bank', 'cash')))
    #
    #         return {
    #             'domain': {'journal_id': domain}}

    # @api.onchange('destination_journal_id')
    # def _onchange_destination_journal_id(self):
    #     if self.env.user.journal_ids and self.env.user.journal_ids and self.env.user.has_group(
    #             'dvit_account_journal_restrict.journal_restrict_group'):
    #         domain = []
    #         domain.append(('id', '=', self.env.user.journal_ids.ids))
    #         domain.append(('type', 'in', ('bank', 'cash')))
    #
    #         return {
    #             'domain': {'destination_journal_id': domain}}

    # @api.model
    # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
    #     if self.env.user.has_group('dvit_account_'
    #                                'journal_restrict.journal_restrict_group') and self.env.user.journal_ids:
    #         domain = [('journal_id', 'in', self.env.user.journal_ids.ids)]
    #
    #     return super(Payment, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit,
    #                                             order=order)


class MoveLine(models.Model):
    _inherit = 'account.move.line'
    is_show = fields.Boolean()

    # @api.model
    # def _search(self, domain, offset=0, limit=None, order=None, access_rights_uid=None):
    #     print('yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy')
    #
    #     if self.env.user.has_group(
    #             'dvit_account_journal_restrict.journal_restrict_group') and self.env.user.journal_ids:
    #         domain = [('journal_id', 'in', self.env.user.journal_ids.ids)]
    #         print('xxxxxxxxxxxxxxxxxxxxxxxxxxx', domain)
    #     return super()._search(domain=domain, offset=offset, limit=limit, order=order,
    #                            access_rights_uid=access_rights_uid)

    # @api.model
    # def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
    #     if self.env.user.has_group(
    #             'dvit_account_journal_restrict.journal_restrict_group') and self.env.user.journal_ids:
    #         domain = [('journal_id', 'in', self.env.user.journal_ids.ids)]
    #
    #     return super(MoveLine, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit,
    #                                              order=order)
