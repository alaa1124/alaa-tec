# -*- coding: utf-8 -*-
from odoo import models, fields, api


class LetterGuranteeSetting(models.Model):
    _name = 'guarantee.letter.setting'
    _rec_name = 'name'

    name = fields.Char('Name')

    account_id = fields.Many2one(
        comodel_name='account.account',
        string="Account Debit",
        required=True,
    )

    letter_type = fields.Selection(
        string="Letter Type",
        selection=[
            ('premium', 'Premium'),
            ('final', 'Final'),
            ('deposit', 'Deposit'),
        ]
    )

    bank_expense_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Account Expenses Debit",
        required=True,
    )


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    account_journal_payment_credit_account_id = fields.Many2one(
        related='company_id.account_journal_payment_credit_account_id',
        readonly=False)


class ResCompany(models.Model):
    _inherit = 'res.company'

    account_journal_payment_credit_account_id = fields.Many2one('account.account',
                                                                string='Journal Outstanding Payments')
