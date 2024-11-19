# -*- coding: utf-8 -*-

from odoo import models, fields, api
from num2words import num2words


class statementline(models.Model):
    _inherit = 'account.bank.statement.line'
    recipient_id = fields.Many2one(comodel_name="res.partner", string="المستلم", required=False)

    def amount_to_text(self):
        convert_amount_in_words = num2words(abs(self.amount), lang='ar')
        st="فقط "+convert_amount_in_words+" جنية "
        return st

    def print_receipt(self):
        return self.env.ref('receipt_print.receipt_payment_action2').report_action(self, data={}, config=False)


