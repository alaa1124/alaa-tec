# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # Receive incoming
    # send Outgoing

    def get_collect_form_bank(self):

        move2 = self.env['account.move'].create({
            'date': self.date_collection,
            'ref': "Cheque Num/" + self.cheque_no or '',
            'partner_id': self.partner_id.id or '',
            'name': self._get_payment_name(self.journal_collection, self.date_collection),
            'company_id': self.company_id.id,
            'journal_id': self.journal_collection.id,
            'line_ids': self.create_journal_receive_state_new(self.journal_collection, self.journal_under_collection.default_account_id),
            'cheque_number': self.cheque_no,
            'currency_id': self.currency_id.id,
        })
        move2.action_post()
        self.state_cheque = 'reconciled'
        self._get_reconsile(self.journal_under_collection.default_account_id)
        return move2

    def create_journal_receive_state_new(self, journal, credit_account):
        lines = []
        if self.state_cheque == 'payment_vendor' and self.vendor_id:
            second_journal_line = {
                'account_id': credit_account.id,
                'partner_id': self.vendor_id.id,
                'name': self.cheque_ref,
                'ref': self.cheque_no,
                'date_maturity': self.effective_date,
                'debit': 0,
                'credit': self.amount,
            }
        else:
            second_journal_line = {
                'account_id': credit_account.id,
                'partner_id': self.partner_id.id,
                'name': self.cheque_ref,
                'ref': self.cheque_no,
                'date_maturity': self.effective_date,
                'debit': 0,
                'credit': self.amount,
            }
        lines.append((0, 0, second_journal_line))
        default_account_id = self.env['account.account']
        print(">>>>>send<<<<<<<<<",self.type_cheq)
        if self.type_cheq == 'recieve_chq':
            print(">>>>>>>>>>>", self.journal_collection.company_id.account_journal_payment_debit_account_id.name)
            if self.journal_collection.use_outstanding:
                if not self.journal_collection.company_id.account_journal_payment_debit_account_id:
                    raise ValidationError(_("Enter Outstanding Accounts"))
                default_account_id = self.journal_collection.company_id.account_journal_payment_debit_account_id
            else:
                default_account_id = self.journal_collection.default_account_id
        first_journal_line = {
            'account_id': default_account_id.id,
            'partner_id': self.partner_id.id,
            'name': self.cheque_ref,
            'ref': self.cheque_no,
            'date_maturity': self.effective_date,
            'debit': self.amount,
            'credit': 0,
        }
        lines.append((0, 0, first_journal_line))

        return lines


    def get_collect_form_bank_send_cheque(self):

        move2 = self.env['account.move'].create({'date': self.date_collection,
                                                 'ref': "Cheque Num/" + self.cheque_no or '',
                                                 'partner_id': self.partner_id.id or '',
                                                 'name': self._get_payment_name(self.journal_collection,self.date_collection),
                                                 'company_id': self.company_id.id,
                                                 'journal_id': self.journal_collection.id,
                                                 'line_ids': self.create_journal_send_state_new(
                                                     self.journal_collection,
                                                     self.journal_id.default_account_id),
                                                 'cheque_number': self.cheque_no,
                                                 'currency_id': self.currency_id.id,

                                                 })

        # if not self.journal_id.post_at_bank_rec:
        move2.action_post()
        self.state_cheque2 = 'reconciled'
        # self.get_employee_recieve()
        self._get_reconsile(self.journal_id.default_account_id)
        return move2


    def create_journal_send_state_new(self, journal, debit_account):
        lines = []
        default_account_id = self.env['account.account']
        if self.type_cheq == 'send_che':
            print(">>>>>>>send>>>>", self.journal_collection.company_id.account_journal_payment_credit_account_id.name)
            if self.journal_collection.use_outstanding:
                if not self.journal_collection.company_id.account_journal_payment_credit_account_id:
                    raise ValidationError(_("Enter Outstanding Accounts"))
                default_account_id = self.journal_collection.company_id.account_journal_payment_credit_account_id
            else:
                default_account_id = journal.default_account_id.id
        second_journal_line = {
            'account_id': debit_account.id,
            'partner_id': self.partner_id.id,
             'name': self.cheque_ref,
            'ref':self.cheque_no,
            'date_maturity': self.effective_date,
            'debit': self.amount,
            'credit': 0,
            'currency_id': self.currency_id.id,'amount_currency':self.amount
        }
        lines.append((0, 0, second_journal_line))
        first_journal_line = {
            'account_id': default_account_id.id,
            'partner_id': self.partner_id.id,
             'name': self.cheque_ref,
            'ref':self.cheque_no,
            'date_maturity': self.effective_date,
            'debit': 0,
            'credit': self.amount,
            'currency_id': self.currency_id.id,'amount_currency':-self.amount
        }
        lines.append((0, 0, first_journal_line))

        return lines
