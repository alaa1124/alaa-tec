from datetime import datetime

from odoo import fields, models
from odoo.exceptions import UserError, ValidationError


class wizard(models.TransientModel):
    _inherit = "eng.wizard"

    def create_eng_line(self, line):
        line = super().create_eng_line(line)
        line.analytic_distribution = self.eng_id.analytic_distribution
        print(line)
        return line


class EngineerTemplate(models.Model):
    _name = 'project.engineer.techincal'
    _inherit = ['project.engineer.techincal', 'analytic.mixin']

    analytic_distribution = fields.Json(required=True)

    def action_draft(self):
        res = super().action_draft()
        move_id = self.env['account.move'].search([('eng_id', '=', self.id)])
        for rec in move_id:
            if rec.state != 'draft':
                raise ValidationError("You cann't reset template because have one of invoice")
            else:
                rec.unlink()
        return res

    def action_view_invoice(self):
        if self.type == 'owner':
            action = self.env['ir.actions.actions']._for_xml_id('account.action_move_line_form')
            action['context'] = {
                'default_partner_id': self.project_id.partner_id.id if self.project_id.partner_id else '',
                'default_project_id': self.project_id.id if self.project_id else '',
                'default_contract_id': self.contract_id.id if self.contract_id else '',
                'default_type': self.type,
                'default_sub_type': self.sub_type,
                'default_eng_id': self.id,
                'default_move_type': 'out_invoice', 'default_type': 'owner',

            }
            action['domain'] = [('eng_id', '=', self.id)]
            return action
        else:
            action = self.env['ir.actions.actions']._for_xml_id('account.action_move_line_form')
            action['context'] = {
                'default_partner_id': self.project_id.partner_id.id if self.project_id.partner_id else '',
                'default_project_id': self.project_id.id if self.project_id else '',
                'default_contract_id': self.contract_id.id if self.contract_id else '',
                'default_type': self.type,
                'default_sub_type': self.sub_type,
                'default_eng_id': self.id,
                'default_move_type': 'out_invoice', 'default_type': 'subconstructor'
            }
            action['domain'] = [('eng_id', '=', self.id)]
            return action

    def action_confirm(self):
        invoice_line_ids = []
        deduction_ids = []
        allowance_ids = []

        for rec in self.deduction_ids:
            deduction_ids.append((0, 0, {
                'contract_type': rec.contract_type,
                'name': rec.name.id,
                'is_precentage': rec.is_precentage,
                'percentage': rec.percentage,
                'value': rec.value,
                'counterpart_account_id': rec.counterpart_account_id.id
            }))
        for rec in self.allowance_ids:
            allowance_ids.append((0, 0, {
                'contract_type': rec.contract_type,
                'name': rec.name.id,
                'is_precentage': rec.is_precentage,
                'percentage': rec.percentage,
                'value': rec.value,
                'counterpart_account_id': rec.counterpart_account_id.id,

            }))
        for rec in self.line_ids:
            if rec.display_type == False:
                invoice_line_ids.append((0, 0, {

                    'detailed_line': rec.stage_line.id,
                    'analytic_distribution': rec.analytic_distribution,
                    'item': rec.stage_line.item.id,
                    'item_line': rec.stage_line.item_line.id,
                    'stage_id': rec.stage_id.id,
                    'quantity': rec.qty,
                    'name': rec.name,
                    'price_unit': rec.differance / rec.qty if rec.qty > 0 else 0,
                    'tax_ids': [],
                    'account_id': self.contract_id.revenue_account_id.id,
                    'display_type':'product' if not rec.display_type else rec.display_type
                }))

        partner_id = False
        if self.contract_id.partner_id and self.type == 'owner':

            partner_id = self.contract_id.partner_id.id
        elif self.contract_id.subcontractor and self.type != 'owner':
            partner_id = self.contract_id.subcontractor.id


        if partner_id:
            print(self.analytic_distribution)
            move_id = self.env['account.move'].with_context(analytic_distribution=True).create({
                'partner_id': partner_id,
                'project_id': self.project_id.id if self.project_id else '',
                'contract_id': self.contract_id.id if self.contract_id else '',
                'type': self.type,
                'sub_type': self.sub_type,
                'move_type': 'out_invoice' if self.type == 'owner' else 'in_invoice',
                'eng_id': self.id,
                'invoice_line_ids': invoice_line_ids,
                'analytic_distribution': self.analytic_distribution,
                'allowance_ids': allowance_ids,
                'deduction_ids': deduction_ids,
            })

        self.state = 'confirm'


class Lines(models.Model):
    _name = "engineer.techincal.lines"
    _inherit = ['engineer.techincal.lines', 'analytic.mixin']

