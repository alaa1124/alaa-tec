# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class Extendurantee(models.Model):
    _name = 'guarantee.extension'
    _rec_name = 'number'
    _inherit = ["mail.thread"]

    number = fields.Char('Sequence')
    letter_guarantee_id = fields.Many2one(comodel_name='guarantee.letter', string="Gurantee Letter",
                                          domain=[('is_close', '=', False)])

    state = fields.Selection(string="State", selection=[('draft', 'Draft'),
                                                        ('confirm', 'Confirm'),
                                                        ('cancel', 'Cancel')
                                                        ], required=False, default="draft")

    partner_id = fields.Many2one(related='letter_guarantee_id.partner_id', string='Customer',
                                 comodel_name='res.partner')
    analytic_id = fields.Many2one(related='letter_guarantee_id.analytic_id', string='Expenses Analytic Account')

    journal_id = fields.Many2one(related='letter_guarantee_id.journal_id', string='Bank')
    letter_type = fields.Selection(string="Letter Type", related='letter_guarantee_id.letter_type')
    letter_amount = fields.Float('Letter Amount', related='letter_guarantee_id.letter_amount')
    bank_expense_account_id = fields.Many2one('account.account', string="Account Expenses Debit")

    transaction_date = fields.Date(string="Transaction Date", related='letter_guarantee_id.transaction_date')
    start_date = fields.Date(string="Start Date", related='letter_guarantee_id.start_date')
    end_date = fields.Date(string="End Date", related='letter_guarantee_id.end_date')
    letter_number = fields.Char('Letter Number', related='letter_guarantee_id.letter_number')
    raise_amount = fields.Float('Raise Amount', compute='compute_amount')
    total_amount = fields.Float('Total Amount', compute='compute_amount')
    expenses_amount = fields.Float('Expenses Amount', )
    extend_start_date = fields.Date(string='Extend Start Date', )
    extend_end_date = fields.Date('Extend End Date')
    note = fields.Text('Note')
    config_id = fields.Many2one(related='letter_guarantee_id.config_id', string='Letter Name')
    is_expenses = fields.Boolean('Is Expense')
    expenses_amount = fields.Float('Expenses Amount')
    expenses_id = fields.Many2one('account.move', 'Expenses Journal')
    is_close = fields.Boolean('Is Closed', compute='compute_closed')

    @api.depends('letter_guarantee_id')
    def compute_closed(self):
        for rec in self:
            letter = self.env['guarantee.letter'].search([('id', '=', rec.letter_guarantee_id.id)])
            rec.is_close = all(l.is_close for l in letter)

    @api.onchange('letter_guarantee_id')
    def onchange_date(self):
        for rec in self:
            dat = self.env['guarantee.extension'].search(
                [('letter_guarantee_id', '=', rec.letter_guarantee_id.id)], limit=1,
                order='create_date desc')
            if dat:
                rec.extend_start_date = dat.extend_end_date
            else:
                letter_guarantee = self.env['guarantee.letter'].search([('id', '=', rec.letter_guarantee_id.id)])
                rec.extend_start_date = letter_guarantee.end_date

    # @api.constrains('letter_guarantee_id')
    # def _compute_date(self):
    #     for rec in self:
    #         dat = self.env['guarantee.extension'].search(
    #             [('id', '!=', rec.id),('letter_guarantee_id', '=', rec.letter_guarantee_id.id)], limit=1,
    #             order='create_date desc')

    #         if dat:
    #             rec.extend_start_date = dat.extend_end_date

    #
    #         else:
    #             letter_guarantee = self.env['guarantee.letter'].search([('id', '=', rec.letter_guarantee_id.id)])
    #             rec.extend_start_date = letter_guarantee.end_date

    @api.depends('letter_guarantee_id')
    def compute_amount(self):
        for rec in self:
            raise_guarantee = self.env['guarantee.increase'].search(
                [('letter_guarantee_id', '=', rec.letter_guarantee_id.id)])
            x = 0.0
            for lin in raise_guarantee:
                x = x + lin.raise_amount
            rec.raise_amount = x
            rec.total_amount = rec.raise_amount + rec.letter_amount

    @api.constrains('extend_end_date', 'end_date')
    def check_date_fields(self):
        dat = self.env['guarantee.extension'].search([('id', '!=', self.id), ])
        # Hashed By Moataz for temp reason to avoid bug on 10102022
        #    if dat:
        #        for line in dat:
        #            if self.extend_end_date <= line.extend_end_date:
        #                raise UserError(_('Extend End Date Must Be Greater Than The End Date'))
        #            else:
        #                pass

        if self.extend_end_date and self.end_date:

            if self.extend_end_date <= self.end_date and self.extend_end_date <= self.extend_start_date:
                raise UserError(_('Extend End Date Must Be Greater Than End Date'))

    def cancel_button(self):
        for rec in self:
            if rec.expenses_id:
                rec.expenses_id.button_cancel()
                # rec.expenses_id.unlink()
            rec.state = 'cancel'

    def confirm_button(self):
        for rec in self:
            if rec.is_expenses:
                config = self.env['guarantee.letter.setting'].search([('id', '=', rec.config_id.id)])
                move = self.env['account.move'].create({
                    'journal_id': rec.journal_id.id,
                    'date': rec.start_date,
                })
                self.env['account.move.line'].with_context(check_move_validity=False).create(
                    {
                        'move_id': move.id,
                        'account_id': config.bank_expense_account_id.id,
                        'name': 'Extend Gurantee Letter',
                        'analytic_account_id': rec.analytic_id.id,
                        'debit': rec.expenses_amount,
                    })
                account_id = ''
                if rec.journal_id.company_id.account_journal_payment_credit_account_id:
                    account_id = rec.journal_id.company_id.account_journal_payment_credit_account_id.id
                else:
                    account_id = rec.journal_id.default_account_id.id
                self.env['account.move.line'].with_context(check_move_validity=False).create(
                    {
                        'move_id': move.id,
                        'account_id': account_id,
                        'analytic_account_id': rec.analytic_id.id,
                        'name': 'Extend Gurantee Letter',
                        'credit': rec.expenses_amount,
                    })
                move.action_post()
                rec.expenses_id = move.id
            rec.state = "confirm"

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('guarantee.extension') or '/'
        vals['number'] = seq
        return super(Extendurantee, self).create(vals)

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError("You cann't delete only draft")
        res = super(Extendurantee, self).unlink()
        return res

    def action_draft(self):
        self.state = 'draft'
