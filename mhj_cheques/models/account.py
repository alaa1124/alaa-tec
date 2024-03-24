
from odoo import _, api, fields, models
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)


class AutomaticEntryWizard(models.TransientModel):
    _inherit = 'account.automatic.entry.wizard'

    # fuck the stupid
    journal_id = fields.Many2one(domain="[('company_id', '=', company_id)]",)


class BankStatment(models.Model):
    _inherit = 'account.bank.statement'

    is_cheque = fields.Boolean(string='Cheque', related='journal_id.is_cheque')

    def check_confirm_bank(self):
        res = super().check_confirm_bank()
        for line in self.line_ids.filtered(lambda l: l.is_cheque):
            amls = self.env['account.move.line']
            amls += line.journal_entry_ids
            payments = self.env['account.payment']
            for aml in amls:
                payments |= aml.payment_id
            amls.write({
                'is_cheque': line.is_cheque,
                'cheque_bank': line.cheque_bank.id,
                'cheque_date': line.date,
                'cheque_no': line.cheque_no,
            })
            payments.write({
                'is_cheque': line.is_cheque,
                'cheque_bank': line.cheque_bank.id,
                'cheque_date': line.date,
                'cheque_no': line.cheque_no,
            })

        # account.bank.statement.line
        for line in self.line_ids.filtered(lambda l: l.analytic_account_id):
            for l in line.journal_entry_ids:  # account.move.line
                if line.account_id == l.account_id:
                    l.analytic_account_id = line.analytic_account_id.id
                    aal = self.env['account.analytic.line'].search([('name', '=', l.name), ('account_id', '=', line.analytic_account_id.id)], order='id desc', limit=1)
                    aal.amount *= -1

        return res


class BankStatmentLine(models.Model):
    _inherit = 'account.bank.statement.line'

    is_cheque = fields.Boolean(string='Cheque', related='statement_id.is_cheque', store=True)
    cheque_bank = fields.Many2one("res.bank", "Cheque Bank")
    cheque_no = fields.Char(string="Cheque No", )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    is_cheque = fields.Boolean(string="Is Cheque")
    cheque_bank = fields.Many2one(string="Cheque Bank", comodel_name="res.bank")
    cheque_date = fields.Date(string="Cheque Date")
    cheque_no = fields.Char(string="Cheque No")

    @api.constrains('payment_id', 'journal_id', 'statement_id', 'full_reconcile_id')
    def set_is_chq(self):
        for aml in self:
            is_cheque = False
            if aml.statement_id:
                stml = aml.statement_line_id
                is_cheque = aml.statement_id.journal_id.is_cheque
                aml.cheque_bank = stml.cheque_bank
                aml.cheque_no = stml.cheque_no
                aml.cheque_date = stml.date
                # aml.date_maturity = stml.date
                for line in aml.move_id.line_ids.filtered(lambda l: not l.statement_id):
                    line.statement_id = aml.statement_id
                    line.statement_line_id = aml.statement_line_id
            if aml.payment_id:
                pay = aml.payment_id
                is_cheque = pay.is_cheque or aml.statement_id.journal_id.is_cheque
                aml.cheque_bank = pay.cheque_bank
                aml.cheque_no = pay.cheque_no
                aml.cheque_date = pay.cheque_date
                # aml.date_maturity = pay.cheque_date
                for line in aml.move_id.line_ids.filtered(lambda l: not l.payment_id):
                    line.payment_id = aml.payment_id
            if aml.full_reconcile_id:
                # chq = aml.full_reconcile_id.reconciled_line_ids.mapped('move_id.line_ids').filtered(lambda l: l.is_cheque).sorted(key=lambda l: l.id)[:1]
                chq = aml.full_reconcile_id.reconciled_line_ids.mapped('move_id.line_ids').filtered(lambda l: l.is_cheque)[1:]
                # chq = all_amls.search([('is_cheque','=',True),('cheque_no','!=',False),],order='id asc', limit=1)
                # _logger.error(f'>>>>>>>>>>>> all amls: {all_amls}')
                # _logger.error(f'>>>>>>>>>>>> chq: {chq}')
                # chq = aml.full_reconcile_id.reconciled_line_ids.mapped('move_id.line_ids.full_reconcile_id.reconciled_line_ids.move_id.line_ids').filtered(lambda l: l.is_cheque)
                # chq = aml.full_reconcile_id.reconciled_line_ids.mapped('move_id.line_ids').filtered(lambda l: l.is_cheque)
                if chq:
                    # chq = chq.search([],order='id asc', limit=1)
                    chq = chq[:1]
                    is_cheque = chq.is_cheque
                    aml.move_id.line_ids.filtered(
                        lambda l: l.account_id.user_type_id.internal_group in ['asset','liability']
                        ).write({
                        'is_cheque': is_cheque,
                        'cheque_bank': chq.cheque_bank,
                        'cheque_date': chq.cheque_date,
                        'date_maturity': chq.cheque_date,
                        'cheque_no': chq.cheque_no,
                    })
            # finally set is_cheque from journal ?
            # aml.is_cheque = is_cheque or aml.journal_id.is_cheque


class AccountPayment(models.Model):
    _inherit = "account.payment"

    communication = fields.Char(string="Payment Reference", )
    cheque_no = fields.Char(string="Cheque No")
    cheque_bank = fields.Many2one("res.bank", "Cheque Bank")
    cheque_date = fields.Date(string="Cheque Date",)
    cheque_journal_id = fields.Many2one(
        string="Journal",
        comodel_name="account.journal",
    )
    is_cheque = fields.Boolean(string="Is Cheque", )
    file = fields.Binary(string="Attachment",)

    _sql_constraints = [
        ('chq_no_uniq', 'unique (cheque_no)',
         'The cheque number must be unique.!'),
    ]

    @api.depends('cheque_journal_id')
    @api.onchange('cheque_journal_id', 'currency_id')
    def _change_journal(self):
        for pay in self:
            if pay.cheque_journal_id:
                pay.journal_id = pay.cheque_journal_id
            # pay.currency_id = pay.journal_id.currency_id or pay.company_id.currency_id


class AccountJournal(models.Model):
    _inherit = "account.journal"

    is_cheque = fields.Boolean(
        string="Cheques?",
        help="This journal will be a cheque wallet, and must be of cash type."
        )

    @api.constrains('is_cheque')
    @api.onchange('is_cheque')
    def is_cheque_changed(self):
        for jo in self.filtered(lambda j: j.is_cheque):
            jo.type = 'cash'
            jo.default_account_id.is_cheque = jo.is_cheque


    @api.constrains('type')
    @api.onchange('type')
    def type_changed(self):
        for jo in self.filtered(lambda j: j.is_cheque and j.type != 'cash'):
            jo.is_cheque = False

    # @api.constrains('default_account_id', 'type', 'is_cheque')
    # def account_changed(self):
    #     for jo in self.filtered(
    #         lambda j: j.is_cheque and j.default_account_id and not j.default_account_id.reconcile):
    #         raise UserError('Cheque journals must link to accounts that reconcile.')


class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_cheque = fields.Boolean(string='Cheques')

