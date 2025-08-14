# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    use_outstanding = fields.Boolean(string='Use Outstanding')
