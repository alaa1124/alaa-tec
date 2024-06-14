from odoo import fields, models, api


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'
    item = fields.Many2one("project.item")

    project_id = fields.Many2one("project.project")
    contract_id = fields.Many2one("project.contract")

    def _select(self):
        return super()._select() + ", move.project_id as project_id, move.contract_id as contract_id, line.item as item"