from odoo import api, fields, models, _


class BankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    account_id = fields.Many2one('account.account', string='Account')


class Move(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(Move, self).action_post()
        for record in self:
            for rec in record.line_ids:
                if rec.statement_line_id:
                    if rec.account_id != rec.journal_id.default_account_id:
                        if rec.statement_line_id.account_id:
                            rec.account_id = rec.statement_line_id.account_id.id
        return res
