from odoo import fields, models, api,_

from odoo.exceptions import UserError, ValidationError
class Contract(models.Model):
    _inherit = 'project.contract'
    count_template = fields.Integer(compute='get_eng_template_id')

    def action_view_Template(self):

        return {
            'name': _('Engineer Template'),
            'view_mode': 'tree,form',
            'res_model': 'project.engineer.techincal',
            'domain': [('contract_id', '=', self.id)],
            'context': {
                'default_project_id': self.project_id.id, \
                'default_contract_id': self.id, \
                'default_subcontractor': self.subcontractor.id if self.subcontractor else '', \
                'default_type': self.type, \
                },
            'target': 'current',
            'type': 'ir.actions.act_window',
        }


    def get_eng_template_id(self):
        for rec in self:
            rec.count_template=0
            if rec.id:
                rec.count_template = len(self.env['project.engineer.techincal'].search([('contract_id', '=', rec.id)]))


    def action_draft(self):
        eng_template_id = self.env['project.engineer.techincal'].search([('contract_id','=',self.id)])
        if eng_template_id:
            raise ValidationError("this contract have engineer Template")
        else:
            self.state='draft'



