from odoo import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        # Call the original `action_post` method to confirm the invoice
        res = super(AccountMove, self).action_post()

        # Update journal item labels for all confirmed invoices
        for move in self:
            journal_items = self.env['account.move.line'].search([('move_id', '=', move.id)])
            for line in journal_items:
                # Customize the label update logic as needed
                line.name = f"{line.name} - Updated"

        return res
