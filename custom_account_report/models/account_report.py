from odoo import models

class GeneralLedgerReport(models.Model):
    _inherit = 'account.report'

    def _get_styles(self):
        styles = super()._get_styles()
        # Customize font size
        styles.update({
            'font_size': 50 ,  # Change font size as needed
        })
        return styles
