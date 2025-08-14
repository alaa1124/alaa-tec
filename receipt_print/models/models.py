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



class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    # طابقي نفس التوقيع الموجود في سورس أودو
    def _build_wkhtmltopdf_args(
        self,
        paperformat_id,
        landscape,
        specific_paperformat_args=None,
        set_viewport_size=False,
    ):
        # خدي القائمة الأصلية من السوبر
        args = super()._build_wkhtmltopdf_args(
            paperformat_id,
            landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )

        # أضيفي/ثبّتي الترميز UTF-8
        try:
            i = args.index("--encoding")
            if i + 1 < len(args):
                args[i + 1] = "utf-8"
        except ValueError:
            args.extend(["--encoding", "utf-8"])

        return args
