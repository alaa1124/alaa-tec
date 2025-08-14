# -*- coding: utf-8 -*-

from operator import contains
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class Extendurantee(models.Model):
    _name = 'guarantee.reduction'
    _rec_name = 'number'

    number = fields.Char('Sequence')
    letter_guarantee_id = fields.Many2one(comodel_name='guarantee.letter', string="Gurantee Letter",
                                          domain=[('is_close', '=', False)])

    state = fields.Selection(string="State", selection=[('draft', 'Draft'),
                                                        ('confirm', 'Confirm'),
                                                        ('cancel', 'Cancel')
                                                        ], required=False, default="draft")

    partner_id = fields.Many2one(related='letter_guarantee_id.partner_id', string='Customer',
                                 comodel_name='res.partner')

    journal_id = fields.Many2one(related='letter_guarantee_id.journal_id', string='Bank')
    letter_type = fields.Selection(string="Letter Type", related='letter_guarantee_id.letter_type')
    letter_raise_amount = fields.Float(string='Letter  Amount', related='letter_guarantee_id.letter_amount')
    letter_amount = fields.Float(string='Net Letter Amount', compute='compute_amount')
    bank_expense_account_id = fields.Many2one('account.account', string="Account Expenses Debit")
    config_id = fields.Many2one(related='letter_guarantee_id.config_id', string='Letter Name')
    move_id = fields.Many2one('account.move', 'Down Journal')
    expenses_id = fields.Many2one('account.move', 'Expenses Journal')
    analytic_id = fields.Many2one(related='letter_guarantee_id.analytic_id', string='Expenses Analytic Account')

    transaction_date = fields.Date(string="Transaction Date", related='letter_guarantee_id.transaction_date')
    start_date = fields.Date(string="Start Date", related='letter_guarantee_id.start_date')
    # start_date = fields.Date(string="Start Date")
    date = fields.Date(string="Date", required=False)
    end_date = fields.Date(string="End Date", related='letter_guarantee_id.end_date')
    letter_number = fields.Char('Letter Number', related='letter_guarantee_id.letter_number')
    raise_amount = fields.Float('Raise Amount', compute='compute_amount')
    down_amount_total = fields.Float('Total Down Amount', compute='compute_amount')
    is_expenses = fields.Boolean('Is Expense')
    expenses_amount = fields.Float('Expenses Amount', )
    cover_amount_percentage = fields.Float('Cover Percentage %')
    cover_amount = fields.Float('Cover Amount ')
    down_amount = fields.Float('Down Amount')
    extend_start_date = fields.Date(string='Last Extend Start Date', compute='compute_date')
    extend_end_date = fields.Date('Last Extend End Date', compute='compute_date')
    note = fields.Text('Note')
    is_close = fields.Boolean('Is Closed', related='letter_guarantee_id.is_close')

    @api.depends('letter_guarantee_id')
    def compute_date(self):
        for rec in self:
            dat = self.env['guarantee.extension'].search([('letter_guarantee_id', '=', rec.letter_guarantee_id.id)],
                                                         limit=1,
                                                         order='create_date desc')
            rec.extend_start_date = dat.extend_start_date
            rec.extend_end_date = dat.extend_end_date

    @api.depends('letter_guarantee_id')
    def compute_closed(self):
        for rec in self:
            letter = self.env['guarantee.letter'].search([('id', '=', rec.letter_guarantee_id.id)])
            rec.is_close = all(l.is_close for l in letter)

    @api.onchange('cover_amount')
    def _onchange_cover_amount(self):
        for rec in self:
            # continue
            if rec.letter_amount:
                rec.cover_amount_percentage = rec.cover_amount / rec.down_amount * 100

    @api.onchange('cover_amount_percentage')
    def _onchange_cover_amount_percentage(self):
        for rec in self:
            # continue
            if rec.letter_amount:
                rec.cover_amount = rec.down_amount * rec.cover_amount_percentage / 100

    @api.onchange('letter_guarantee_id')
    @api.constrains('letter_guarantee_id')
    def compute_amount(self):
        for rec in self:
            if rec.letter_guarantee_id:
                raise_guarantee = self.env['guarantee.increase'].search(
                    [('letter_guarantee_id', '=', rec.letter_guarantee_id.id)])
                down_guarantee = self.env['guarantee.reduction'].search(
                    [('letter_guarantee_id', '=', rec.letter_guarantee_id.id)])
                x = 0.0
                for rais in raise_guarantee:
                    x = x + rais.raise_amount
                rec.raise_amount = x
                dwn = 0.0
                for dwo in down_guarantee:
                    dwn = dwn + dwo.down_amount
                    rec.down_amount_total = dwn
                letter = self.env['guarantee.letter'].search([('id', '=', rec.letter_guarantee_id.id)])
                y = 0.0
                for let in letter:
                    y = y + let.letter_amount
                rec.letter_amount = x + y - rec.down_amount_total
                if rec.letter_amount < 0:
                    raise UserError(_('Down Must be less than letter and raise amount'))

    def cancel_button(self):
        for rec in self:
            dwn = self.env['guarantee.reduction'].search([('letter_guarantee_id', '=', rec.letter_guarantee_id.id)])
            for lin in dwn:

                if rec.id < lin.id:
                    raise ValidationError(_('You Must Cancel Last Down Before'))

            if rec.move_id:
                rec.move_id.button_cancel()

            if rec.expenses_id:
                rec.expenses_id.button_cancel()
                # rec.expenses_id.unlink()
            rec.state = 'cancel'

    def action_draft(self):
        self.state = 'draft'

    def confirm_button(self):
        for rec in self:
            config = self.env['guarantee.letter.setting'].search([('id', '=', rec.config_id.id)])
            move = self.env['account.move'].create({
                'journal_id': rec.journal_id.id,
                'date': rec.date,
            })
            self.env['account.move.line'].with_context(check_move_validity=False).create(
                {
                    'move_id': move.id,
                    'account_id': config.account_id.id,
                    'name': 'Down Gurantee Letter',
                    'credit': rec.cover_amount,
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
                    'name': 'Down Gurantee Letter',
                    'debit': rec.cover_amount,
                })
            move.action_post()
            rec.move_id = move.id
            if rec.is_expenses:
                config = self.env['guarantee.letter.setting'].search([('id', '=', rec.config_id.id)])
                move = self.env['account.move'].create({
                    'journal_id': rec.journal_id.id,
                    'date': rec.date,
                })
                self.env['account.move.line'].with_context(check_move_validity=False).create(
                    {
                        'move_id': move.id,
                        'account_id': config.bank_expense_account_id.id,
                        'name': 'Gurantee Letter',
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
                        'name': 'Gurantee Letter',
                        'analytic_account_id': rec.analytic_id.id,
                        'credit': rec.expenses_amount,
                    })
                move.action_post()
                rec.expenses_id = move.id
            rec.state = "confirm"

    @api.constrains('cover_amount')
    def _cover_amount(self):
        for rec in self:
            if rec.cover_amount:
                raise_guarantee = self.env['guarantee.increase'].search(
                    [('letter_guarantee_id', '=', rec.letter_guarantee_id.id)])
                x = 0.0
                for rais in raise_guarantee:
                    x = x + rais.cover_amount
                letter = self.env['guarantee.letter'].search([('id', '=', rec.letter_guarantee_id.id)])
                y = 0.0
                for let in letter:
                    y = y + let.cover_amount
                down_guarantee = self.env['guarantee.reduction'].search(
                    [('letter_guarantee_id', '=', rec.letter_guarantee_id.id)])
                dwn = 0.0
                dwn_total = 0.0
                for dwo in down_guarantee:
                    dwn = dwn + dwo.cover_amount
                    dwn_total = dwn_total + dwo.cover_amount
                    if dwn > x + y:
                        raise UserError(_('Down Must be less than letter and raise Cover amount'))

                    # if rec.cover_amount > (x + y - dwn_total + rec.cover_amount):
                    #     # Adjusted logic to compare current reduction's cover_amount against remaining cover
                    #     raise UserError(
                    #         _('Cover reduction amount cannot exceed the current net cover amount.'))  # Changed Warning to UserError and rephrased

    # @api.constrains('down_amount')
    # def _down_amount(self):
    #     if self.down_amount:

    #         if self.down_amount > (self.letter_amount):
    #             raise UserError(_('Down Must be less than letter and raise amount'))

    # @api.constrains('letter_guarantee_id')
    # def _letter_guarantee_id(self):
    #     if self.letter_guarantee_id:
    #         x=0.0
    #         downs = self.env['guarantee.reduction'].search(
    #             [('letter_guarantee_id', '=', self.letter_guarantee_id.id)])
    #         for rec in downs:
    #             x = x + rec.down_amount
    #             if x > (self.letter_amount +self.raise_amount):
    #                 raise UserError(_('Down Gurantee For this Gurantee Letter Over than Gurantee Letter Amount'))

    @api.model
    def create(self, vals):
        if 'date' not in vals:
            vals['date'] = fields.Date.today()
        seq = self.env['ir.sequence'].next_by_code('guarantee.reduction') or '/'
        vals['number'] = seq
        return super(Extendurantee, self).create(vals)

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError("You cann't delete only draft")
        res = super(Extendurantee, self).unlink()
        return res
