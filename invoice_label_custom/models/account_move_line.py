
from odoo import models, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def update_labels(self, move_id, new_label):
        # Get all journal items for the specified move (invoice)
        journal_items = self.search([('move_id', '=', move_id)])
        # Update the label for each journal item
        for line in journal_items:
            line.name = f"{line.name} - {new_label}"
        return True
