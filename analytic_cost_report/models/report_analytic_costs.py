from odoo import models, fields, api

class ReportAnalyticCosts(models.AbstractModel):
    _name = 'report.your_module.report_analytic_costs'
    _description = 'Analytic Costs Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.analytic.line'].browse(docids)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'account.analytic.line',
            'data': data,
            'docs': docs,
            'date_today': fields.Date.today(),
        }
