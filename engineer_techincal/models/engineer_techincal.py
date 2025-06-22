from odoo import fields, models, api, _

from datetime import datetime

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


def print_log(*s):
    print(s)
    _logger.info(f"#######################{s}")


class EngineerTemplate(models.Model):
    _name = 'project.engineer.techincal'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'EngineerTemplate'

    def unlink(self):
        for rec in self:
            if rec.state == 'confirm':
                raise UserError('Can not delete confirmed Templates. Set it to draft first')
        return super().unlink()

    name = fields.Char()
    project_id = fields.Many2one("project.project", domain=[('state', '=', 'confirm')], required=True)
    type = fields.Selection([('owner', 'owner'), ('subconstructor', 'subconstructor')], default='owner',
                            string="Type of Contract")
    contract_id = fields.Many2one("project.contract",
                                  domain="[('is_subcontract','=',False),('project_id','=',project_id),('type','=',type)]",
                                  required=True)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], default='draft')
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)

    date = fields.Date(default=datetime.today(), required=True)

    referance = fields.Char()
    sub_type = fields.Selection([('process', 'Process'), ('final', 'Final')], default='process', string="Type",
                                required=True)
    deduction_ids = fields.One2many("engineer.deduction.lines", "engineer_id", )
    allowance_ids = fields.One2many("engineer.allowance.lines", "engineer_id")
    amount_total = fields.Float(compute='get_amount_total')
    amount_total_without_ded_allowance = fields.Float(compute='get_amount_total')
    line_ids = fields.One2many("engineer.techincal.lines", "eng_id")
    total_deduction = fields.Float(compute='get_total_deduction')
    total_allowance = fields.Float(compute='get_total_allowance')
    subcontractor = fields.Many2one("res.partner")

    @api.onchange('project_id')
    def _onchnage_project(self):
        if self.project_id and self.contract_id == 'owner':
            contract_id = self.env['project.contract'].search(
                [('type', '=', self.type), ('project_id', '=', self.project_id.id)], limit=1)
            self.contract_id = contract_id.id if contract_id else ''

    @api.depends('deduction_ids')
    def get_total_deduction(self):
        for rec in self:
            rec.total_deduction = 0
            for line in rec.deduction_ids:
                rec.total_deduction += line.value

    @api.depends('allowance_ids')
    def get_total_allowance(self):
        for rec in self:
            rec.total_allowance = 0
            for line in rec.allowance_ids:
                rec.total_allowance += line.value

    # def unlink(self):
    #     for rec in self:
    #         if rec.state != 'draft':
    #             raise ValidationError("You Cann't delete confirmed ")
    #     res = super(EngineerTemplate, self).unlink()
    #
    #     return res

    def action_confirm(self):
        self.state = 'confirm'

    def action_draft(self):
        for record in self:
            # Find the record with the latest date in the model
            latest_record = self.search([('contract_id', '=', record.contract_id.id),
                                         ('project_id', '=', record.project_id.id), ('state', '=', 'confirm')],
                                        order='date desc', limit=1)
            print_log(latest_record)
            print_log(record)
            # Check if the current record is the one with the latest date
            if record != latest_record:
                raise ValidationError(
                    f"Cannot set the record to 'draft' because it is not the latest record by date. "
                    f"The latest record has the date {latest_record.date}."
                )

            # If the record is the latest, set its state to 'draft'
            record.state = 'draft'

    @api.constrains('date')
    def _check_date_larger_than_others(self):
        for record in self:
            # Search for any record in the model with a date greater than or equal to the current record's date
            existing_record = self.search([
                ('date', '>=', record.date),
                ('contract_id', '=', record.contract_id.id),
                ('project_id', '=', record.project_id.id),
                ('id', '!=', record.id)  # Exclude the current record from the search
            ], limit=1)
            if existing_record:
                raise ValidationError(
                    f"The date {record.date} must be larger than any other date in the model. "
                    f"Found a record with date {existing_record.date}."
                )

    @api.depends('line_ids')
    def get_amount_total(self):
        for record in self:
            record.amount_total = record.amount_total_without_ded_allowance = 0
            if record.line_ids:
                record.amount_total = sum(
                    record.line_ids.mapped('differance')) + record.total_allowance - record.total_deduction
                record.amount_total_without_ded_allowance = sum(
                    record.line_ids.mapped('differance'))
                for ded in record.deduction_ids:
                    ded.onchange_is_precentage()
                for ded in record.allowance_ids:
                    ded.onchange_is_precentage()

    def select_item(self):
        # item_ids = []
        # contract_line_ids = self.env['project.contract.line'] \
        #     .search(['|', ('contract_id', '=', self.contract_id.id),
        #              ('contract_id.parent_contract_id', '=', self.contract_id.id)])
        #
        # for rec in contract_line_ids:
        #     if self.type == 'owner':
        #
        #         if rec.item:
        #             item_ids.append(rec.item.id)
        #     else:
        #         print("========================22222")
        #         if rec.item_sub_id:
        #             item_ids.append(rec.item_sub_id.id)

        return {
            'name': _('Select Item'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'eng.wizard',
            'type': 'ir.actions.act_window',
            'context': {'default_contract_id': self.contract_id.id, \
                        'default_eng_id': self.id},
            'target': 'new',
        }

    @api.onchange('contract_id')
    def _onchnage_subcontractor(self):
        if self.contract_id.subcontractor:
            self.subcontractor = self.contract_id.subcontractor.id

    @api.model
    def create(self, vals):
        res = super(EngineerTemplate, self).create(vals)
        res.name = self.env["ir.sequence"].next_by_code("project.engineer.techincal")

        if res.contract_id.deduction_ids:

            for rec in res.contract_id.deduction_ids:
                line = self.env['engineer.deduction.lines'].create({
                    'engineer_id': res.id,
                    'contract_type': rec.contract_type,
                    'name': rec.name.id,
                    'is_precentage': rec.is_precentage,
                    'percentage': rec.percentage,
                    'value': rec.value,
                    'counterpart_account_id': rec.counterpart_account_id,
                })
                line.onchange_is_precentage()
        if res.contract_id.allowance_ids:
            for rec in res.contract_id.allowance_ids:
                line = self.env['engineer.allowance.lines'].create({
                    'engineer_id': res.id,
                    'contract_type': rec.contract_type,
                    'name': rec.name.id,
                    'is_precentage': rec.is_precentage,
                    'percentage': rec.percentage,
                    'value': rec.value,
                    'counterpart_account_id': rec.counterpart_account_id,
                })
                line.onchange_is_precentage()
        return res


# المستخلص
class Lines(models.Model):
    _name = "engineer.techincal.lines"
    eng_id = fields.Many2one('project.engineer.techincal', ondelete='cascade')
    contract_id = fields.Many2one(related='eng_id.contract_id')
    name = fields.Char(required=True, string="Description")
    item = fields.Many2one(related='stage_line.item', store=True)
    item_line = fields.Many2one(related='stage_line.item_line', store=True)
    stage_id = fields.Many2one("project.stage")
    sequence = fields.Integer(string='Sequence', default=10)
    related_job_id = fields.Many2one("project.related.job")
    uom_id = fields.Many2one("uom.uom", related="item.uom_id")
    qty = fields.Float(string="current Quantity")

    project_contract_line = fields.Many2one('project.contract.line')


    price_unit = fields.Float()
    contract_quanity = fields.Float()
    previous_quanity = fields.Float(store=True, readonly=True)
    total_quanity = fields.Float(compute='get_total_quanity')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False)
    state = fields.Selection(related='eng_id.state', store=True)
    stage_prec = fields.Float(string="% Stage")
    precentage = fields.Float(string="% Percent")
    amount = fields.Float(compute='get_amount')
    price = fields.Float(compute='get_amount')
    previous_amount = fields.Float(store=True, readonly=True)
    differance = fields.Float(compute='get_diff')
    is_pre_update = fields.Boolean()
    type = fields.Selection(related="contract_id.type", default='owner',
                            string="Type of Contract")

    stage_line = fields.Many2one('project.contract.stage.line')

    @api.depends('amount', 'price', 'previous_amount')
    def get_diff(self):
        for rec in self:
            rec.differance = rec.price - rec.previous_amount

    # def write(self, vals):
    #     res =super(Lines,self).write(vals)
    #     if self.previous_amount > 0:
    #
    #         if self.eng_id and self.id and self.stage_id:
    #             lines = self.env['engineer.techincal.lines'].search(
    #                 [('item', '=', self.item.id), ('related_job_id', '=', self.related_job_id.id),
    #                  ('stage_id', '=', self.stage_id.id), ('id', '<', self.id), ('eng_id.state', '=', 'confirm'),
    #                  ('contract_id', '=', self.contract_id.id), ('eng_id', '!=', self.eng_id.id)],
    #                 order='stage_id desc')
    #
    #             self.previous_amount = sum(lines.mapped('price')) - sum(lines.mapped('previous_amount'))
    #     return res

    # @api.depends('item', 'related_job_id', 'stage_id', 'contract_id')
    # def get_previous_amount(self):
    #     for rec in self:
    #         rec.previous_quanity = 0
    #
    #         if rec.eng_id and rec.id and rec.stage_id:
    #             if rec.eng_id.type == 'owner':
    #                 lines = self.env['engineer.techincal.lines'].search(
    #                     [('item', '=', rec.item.id), ('related_job_id', '=', rec.related_job_id.id),
    #                      ('stage_id', '=', rec.stage_id.id), ('id', '<', rec.id), ('eng_id.state', '=', 'confirm'),
    #                      ('contract_id', '=', rec.contract_id.id), ('eng_id', '!=', rec.eng_id.id)],
    #                     order='stage_id desc')
    #             else:
    #                 lines = self.env['engineer.techincal.lines'].search(
    #                     [('item', '=', rec.item.id), ('eng_id.subcontractor', '=', rec.eng_id.subcontractor.id),
    #                      ('related_job_id', '=', rec.related_job_id.id),
    #                      ('stage_id', '=', rec.stage_id.id), ('id', '<', rec.id), ('eng_id.state', '=', 'confirm'),
    #                      ('contract_id', '=', rec.contract_id.id), ('eng_id', '!=', rec.eng_id.id)],
    #                     order='stage_id desc')
    #
    #             rec.previous_quanity = sum(lines.mapped('qty'))
    #             # rec.previous_amount = sum(lines.mapped('price'))-sum(lines.mapped('previous_amount'))
    #             if rec.precentage == 0 and lines and rec.is_pre_update == False:
    #                 rec.precentage = self.env['engineer.techincal.lines'].search(
    #                     [('item', '=', rec.item.id), ('related_job_id', '=', rec.related_job_id.id),
    #                      ('stage_id', '=', rec.stage_id.id), ('id', '<', rec.id), ('eng_id.state', '=', 'confirm'),
    #                      ('contract_id', '=', rec.contract_id.id), ('eng_id', '!=', rec.eng_id.id)], order='id desc',
    #                     limit=1).precentage
    #                 rec.is_pre_update = True
    #             if rec.precentage == 0 and not lines and rec.is_pre_update == False:
    #                 rec.precentage = 100
    #                 rec.is_pre_update = True

    @api.depends('stage_prec', 'total_quanity', 'price_unit', 'precentage')
    def get_amount(self):
        for rec in self:
            rec.amount = (round(rec.price_unit, 2) * rec.total_quanity)
            rec.price = (rec.precentage / 100) * rec.amount

    @api.depends('qty', 'previous_quanity')
    def get_total_quanity(self):
        for rec in self:
            rec.total_quanity = rec.qty + rec.previous_quanity

    # def get_previous_amount_last(self, eng_line):
    #     previous_amount = 0
    #     if self.eng_id and eng_line.id and eng_line.stage_id:
    #         lines = self.env['engineer.techincal.lines'].search(
    #             [('item', '=', eng_line.item.id), ('related_job_id', '=', eng_line.related_job_id.id),
    #              ('stage_id', '=', eng_line.stage_id.id), ('id', '<', eng_line.id), ('eng_id.state', '=', 'confirm'),
    #              ('contract_id', '=', self.eng_id.contract_id.id), ('eng_id', '!=', self.eng_id.id)],
    #             order='stage_id desc')
    #
    #         previous_amount = sum(lines.mapped('price')) - sum(lines.mapped('previous_amount'))
    #         print("============================", previous_amount)
    #     return previous_amount

    @api.model
    def create(self, vals):
        res = super(Lines, self).create(vals)

        # res.previous_amount = self.get_previous_amount_last(res)
        return res

    def get_previous_qty(self):
        recs = self.search([('state', '=', 'confirm'), ('stage_line', '=', self.stage_line.id), ('id', '!=', self.id)])
        self.previous_quanity = sum(recs.mapped('qty'))
        self.previous_amount = sum(recs.mapped('differance'))
        # print(qty)
        # return qty
