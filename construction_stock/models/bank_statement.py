from odoo import models, fields, api


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    project_id = fields.Many2one('project.project')
    item_id = fields.Many2one("project.item", domain="[('id','in',allowed_item_ids)]")
    item_line = fields.Many2one('project.tender', domain="[('project_id','=?',project_id), ('item','=?',item_id)]")
    allowed_item_ids = fields.Many2many("project.item", compute="get_allowed_item_ids")

    @api.depends('project_id')
    def get_allowed_item_ids(self):
        for rec in self:
            rec.allowed_item_ids = []
            if rec.project_id:
                items_ids = self.env['project.tender'].sudo().search(
                    [('project_id', '=', rec.project_id.id)])
                print(">>>>>>>>>>>>>>>.", items_ids)
                for item in items_ids:
                    rec.allowed_item_ids = [(4, item.item.id)]