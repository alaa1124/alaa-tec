
from odoo import models, fields, api, _
import odoo.tools


class res_partner(models.Model):
    _inherit = 'res.partner'
    
    ss_number = fields.Char(string='SSN', required=False, size=50)
    cheque_count = fields.Integer('Cheques',compute="_compute_chqs")
    unit_count = fields.Integer('Units',compute="_compute_units")


    def _compute_chqs(self):
        for r in self:
            chqs = self.env['account.payment'].search([
                ('partner_id', '=', self.id),
                ('is_cheque', '=', True),
                ])
            r.cheque_count = len(chqs)

    def _compute_units(self):
        for r in self:
            chqs = self.env['product.template'].search([
                ('partner_id', '=', self.id),
                ])
            r.unit_count = len(chqs)

    def partner_rs_units(self):
        return{
            'name': _('Units'),
            'type': 'ir.actions.act_window',
            'res_id': 'itsys_real_estate.building_unit_act1',
            'view_mode': 'tree,form',
            'res_model': 'product.template',
            'views': [
                [self.env.ref('itsys_real_estate.building_unit_list').id, 'list'], 
                [self.env.ref('itsys_real_estate.building_unit_form').id, 'form']
                ],
            'domain': [('partner_id', '=', self.id)],
            'context': {}
        }

    def partner_cheques(self):
        action = self.env["ir.actions.act_window"]._for_xml_id('check_management.action_payment_account')
        action['domain'] = [('partner_id', '=', self.id)]
        return action


class res_company(models.Model):
    _inherit = 'res.company'
    id_number=fields.Char(related='partner_id.ss_number')
    
