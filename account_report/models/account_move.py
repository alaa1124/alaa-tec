from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('line_ids.name')
    def _onchange_name(self):
        for move in self:
            for line in move.line_ids:
                if line.name:
                    line.name = f"{line.name} - Updated"

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for move in self:
            for line in move.line_ids:
                if line.name:
                    line.name = f"{line.name} - Updated"

        return res