from odoo import models

class GeneralLedgerReport(models.AbstractModel):
    _inherit = 'account.report'

    def get_html(self, options, line_id=None, additional_context=None):
        html = super().get_html(options, line_id, additional_context)
        # Inject custom styles for font size
        custom_style = "<style>table, th, td { font-size: 50px !important; }</style>"
        html = custom_style + html
        return html
