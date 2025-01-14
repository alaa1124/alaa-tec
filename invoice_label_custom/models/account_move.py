from odoo import models
import logging
_logger = logging.getLogger(__name__)

_logger.info(f"Updating labels for move_id {move_id}")

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        """
        Confirm the invoice and update journal item labels.
        """
        # Call the original action_post method
        result = super(AccountMove, self).action_post()

        # Update labels for journal items after posting the invoice
        for move in self:
            if move.move_type in ['out_invoice', 'in_invoice']:  # Only for invoices
                move.line_ids.update_labels(move.id, "Updated")
        return result
