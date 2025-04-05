from datetime import datetime

from odoo import fields, models
from odoo.exceptions import UserError, ValidationError


class EngineerTemplate(models.Model):
    _inherit = 'project.engineer.techincal'

    def action_draft(self):
        res = super().action_draft()
        move_id = self.env['account.move'].search([('eng_id', '=', self.id)])
        for rec in move_id:

                if rec.state != 'draft':
                    raise ValidationError("You cann't reset template because have one of invoice")
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

        print("=======================================", invoice_line_ids)

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
                print("=========================================3333")
                invoice_line_ids.append((0, 0, {

                    'item': rec.item.id,
                    'stage_id': rec.stage_id.id,
                    'quantity': rec.qty,
                    'name': rec.name,
                    'price_unit': rec.differance / rec.qty if rec.qty > 0 else 0,
                    'tax_ids': [],
                    'account_id': self.contract_id.revenue_account_id.id,
                    'display_type':'product' if not rec.display_type else rec.display_type
                }))

        partner_id = ''
        if self.project_id.partner_id and self.type == 'owner':

            partner_id = self.project_id.partner_id.id
        elif self.contract_id.partner_id and self.type != 'owner':
            partner_id = self.contract_id.subcontractor.id if self.contract_id.subcontractor else ''
        if partner_id:

            move_id = self.env['account.move'].create({
                'partner_id': partner_id,
                'project_id': self.project_id.id if self.project_id else '',
                'contract_id': self.contract_id.id if self.contract_id else '',
                'type': self.type,
                'sub_type': self.sub_type,
                'move_type': 'out_invoice' if self.type == 'owner' else 'in_invoice',
                'eng_id': self.id,
                'invoice_line_ids':invoice_line_ids,

                'allowance_ids': allowance_ids,
                'deduction_ids': deduction_ids,

            })
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>..",move_id.invoice_line_ids,invoice_line_ids)

        self.state = 'confirm'
