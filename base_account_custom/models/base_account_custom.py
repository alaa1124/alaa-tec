# -*- coding: utf-8 -*-

from odoo import _,api, fields, models



class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'analytic.mixin']


class AccountPayment(models.Model):
    _name = 'account.payment'
    _inherit = ['account.payment', 'analytic.mixin']


class AccountMoveLine(models.Model):
    _name = 'account.move.line'
    _inherit = ['account.move.line', 'analytic.mixin']

    analytic_account_id = fields.Many2one('account.analytic.account')

    
