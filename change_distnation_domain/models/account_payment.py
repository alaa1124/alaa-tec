from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from num2words import num2words
import calendar


# default_account_id




class AccountPayment(models.Model):
    _inherit = 'account.payment'

    destination_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Destination Journal',
        domain="[]",
        check_company=True,
    )