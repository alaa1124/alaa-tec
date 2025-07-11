from odoo import models

class EngineerTemplateReport(models.AbstractModel):
    _name = 'report.project_engineer_techincal.engineer_temp_report'
    _description = 'Engineer Template Report'

    def _get_report_values(self, docids, data=None):
        view_id = self.env.context.get('view_id')

        # Detect which view is active
        if view_id == self.env.ref('project_engineer_techincal.action_engineer_template_owner').id:
            report_type = 'owner'
        elif view_id == self.env.ref('project_engineer_techincal.action_engineer_template_subcontarctor').id:
            report_type = 'subcontractor'
        else:
            report_type = 'owner'  # default

        docs = self.env['project.engineer.techincal'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'project.engineer.techincal',
            'docs': docs,
            'report_type': report_type,
        }
