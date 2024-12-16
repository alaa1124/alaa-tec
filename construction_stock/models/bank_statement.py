from odoo import models, fields, api


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    project_id = fields.Many2one('project.project')
    item_id = fields.Many2one('project.item')