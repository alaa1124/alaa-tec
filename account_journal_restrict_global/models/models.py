# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError, AccessError, RedirectWarning


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _search_default_journal(self):
        if self.payment_id and self.payment_id.journal_id:
            return self.payment_id.journal_id
        if self.statement_line_id and self.statement_line_id.journal_id:
            return self.statement_line_id.journal_id
        if self.statement_line_ids.statement_id.journal_id:
            return self.statement_line_ids.statement_id.journal_id[:1]

        journal_types = self.sudo()._get_valid_journal_types()
        company = self.company_id or self.env.company
        domain = [
            *self.env['account.journal'].sudo()._check_company_domain(company),
            ('type', 'in', journal_types),
        ]

        journal = None
        # the currency is not a hard dependence, it triggers via manual add_to_compute
        # avoid computing the currency before all it's dependences are set (like the journal...)
        if self.env.cache.contains(self, self._fields['currency_id']):
            currency_id = self.currency_id.id or self._context.get('default_currency_id')
            if currency_id and currency_id != company.currency_id.id:
                currency_domain = domain + [('currency_id', '=', currency_id)]
                journal = self.env['account.journal'].sudo().search(currency_domain, limit=1)

        if not journal:
            journal = self.env['account.journal'].sudo().search(domain, limit=1)

        if not journal:
            error_msg = _(
                "No journal could be found in company %(company_name)s for any of those types: %(journal_types)s",
                company_name=company.display_name,
                journal_types=', '.join(journal_types),
            )
            raise UserError(error_msg)

        return journal



class Users(models.Model):
    _inherit = 'res.users'

    journal_ids = fields.Many2many(
        'account.journal',
        'users_journals_restrict',
        'user_id',
        'journal_id',
        'Allowed Journals',
    )

    # @api.constrains('journal_ids')
    # def update_journal_restrict(self):
    #     restrict_group = self.env.ref('dvit_account_journal_restrict.journal_restrict_group')
    #     for user in self:
    #         if user.journal_ids:
    #             # add users to restriction group
    #             # Due to strange behaviuor, we must remove the user from the group then
    #             # re-add him again to get restrictions applied
    #             restrict_group.write({'users':  [(3, user.id)]})
    #             user.groups_id =[(3, restrict_group.id)]
    #             ## re-add
    #             restrict_group.write({'users':  [(4, user.id)]})
    #             user.groups_id =[(4, restrict_group.id)]
    #         else:
    #             restrict_group.write({'users':  [(3, user.id)]})
    #             user.groups_id =[(3, restrict_group.id)]

            # self.env.user.context_get().clear_cache(self)
