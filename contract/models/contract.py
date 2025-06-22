# mohamed.abdalrhman0@gmail.com
from datetime import datetime

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class Contract(models.Model):
    _name = 'project.contract'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Contract'
    _rec_name = "name"
    name = fields.Char()
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')], default='draft')
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)

    project_id = fields.Many2one("project.project", string="Project", domain="[('state','=','confirm')]")
    partner_id = fields.Many2one("res.partner")
    type = fields.Selection([('owner', 'owner'), ('subconstructor', 'subconstructor')], default='owner',
                            string="Type of Contract")

    contarct_line_ids = fields.One2many("project.contract.line", "contract_id")

    stage_lines = fields.One2many('project.contract.stage.line', 'contract_id')

    date = fields.Date(default=datetime.today())
    received_date = fields.Date(default=datetime.today())
    contract = fields.Many2one("project.contract.conf", domain="[('type', '=', type)]")
    parent_account_id = fields.Many2one("account.account", string="Partner account",
                                        related='contract.parent_account_id')
    revenue_account_id = fields.Many2one("account.account", string="Cost Account",
                                         related='contract.revenue_account_id')
    amount_total = fields.Float(compute='_compute_amount_total')
    down_payment = fields.Float("Down Payment %")
    down_payment_value = fields.Float("Down Payment ")
    referance = fields.Char()
    deduction_ids = fields.One2many("contract.deduction.lines", "contract_id")
    allowance_ids = fields.One2many("contract.allowance.lines", "contract_id")
    stage_ids = fields.One2many("contract.stage", "contract_id")
    description = fields.Text()
    is_subcontract = fields.Boolean(copy=False)
    parent_contract_id = fields.Many2one("project.contract", copy=False)

    sub_contract_ids = fields.One2many('project.contract', 'parent_contract_id')

    count_subcontract = fields.Integer(compute='get_count_subcontract')
    subcontractor = fields.Many2one("res.partner", domain=[('supplier_rank', '!=', 0)])

    @api.depends('parent_contract_id')
    def get_count_subcontract(self):
        for rec in self:
            rec.count_subcontract = len(self.env['project.contract'] \
                                        .search([('parent_contract_id', '=', self.id)]))

    def create_subcontract(self):

        return {
            'name': 'sub-contract',
            'view_mode': 'form',
            'view_id': self.env.ref('contract.contract_view_form').id,
            'res_model': 'project.contract',
            'context': {
                'default_is_subcontract': True,
                'default_parent_contract_id': self.id,
                'default_contract': self.contract.id,
                'default_project_id': self.project_id.id,
                'default_partner_id': self.partner_id.id,

            },

            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_view_subcontract(self):
        return {
            'name': 'sub-contract',
            'view_mode': 'tree,form',
            'res_model': 'project.contract',
            'domain': [('parent_contract_id', '=', self.id)],
            'target': 'current',
            'type': 'ir.actions.act_window',
        }

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError("You Can't delete confirmed contract")
        res = super(Contract, self).unlink()

        return res

    @api.constrains('stage_ids')
    def _check_stage_ids(self):
        if sum(self.stage_ids.mapped('prec')) != 100 and self.stage_ids:
            raise ValidationError("Percentage stage must be 100")

    @api.onchange('amount_total', 'down_payment')
    def _onchnage_down_payment(self):

        if self.down_payment > 0:
            self.down_payment_value = (self.down_payment / 100) * self.amount_total

    @api.onchange('amount_total', 'down_payment_value')
    def _onchnage_down_payment_value(self):
        if self.down_payment_value > 0:
            self.down_payment = (self.down_payment_value / self.amount_total) * 100 if self.amount_total > 0 else 0

    @api.depends('contarct_line_ids')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = 0
            for rec in record.contarct_line_ids:
                record.amount_total += rec.amount_total

    @api.onchange('project_id')
    def _onchange_project_id(self):
        if self.project_id:
            if self.project_id.partner_id:
                self.partner_id = self.project_id.partner_id.id

    def action_confirm(self):

        self.state = 'confirm'

        if not self.stage_ids and not self.contarct_line_ids.stage_ids:
            raise ValidationError("please add stages")

        self.contarct_line_ids.create_stage_lines()

    @api.onchange('project_id', 'is_subcontract')
    def _onchnage_project_id(self):
        if self.project_id and not self.contarct_line_ids and self.is_subcontract == False and self.type == 'owner':

            tender_ids = self.env['project.tender'].search([('project_id', '=', self.project_id.id)])
            lines = []
            for rec in tender_ids:
                lines.append((0, 0, {
                    'code': rec.code,
                    'name': rec.name,
                    'item': rec.item.id if rec.item else '',
                    'item_line': rec.id,
                    'related_job_id': rec.related_job_id.id if rec.related_job_id else '',
                    'uom_id': rec.uom_id.id if rec.uom_id else '',
                    'qty': rec.qty,
                    'price_unit': rec.price_unit,
                    'tax_ids': [(4, tax.id) for tax in rec.tax_ids] if rec.tax_ids else [],
                    'sequence': rec.sequence,
                    'display_type': rec.display_type,
                }))
            self.contarct_line_ids = lines

    @api.constrains('project_id')
    def check_project_id(self):
        if self.type == 'owner':
            contract_ids = self.env['project.contract'].search(
                [('type', '=', self.type), ('is_subcontract', '=', False),
                 ('project_id', '=', self.project_id.id)])
            if len(contract_ids) > 1:
                raise ValidationError("This Project is created before")

    def action_draft(self):
        self.state = 'draft'
        self.stage_lines.unlink()

    @api.model
    def create(self, vals):
        res = super(Contract, self).create(vals)
        if res.type == 'owner':
            res.name = "Owner Contract" + "/" + res.project_id.name + "/" + self.env["ir.sequence"].next_by_code(
                "contowner")
        else:
            res.name = "Subcontractor Contract" + "/" + res.project_id.name + self.env[
                "ir.sequence"].next_by_code("contsupcontractor")
        return res


# lines with stages
class StageLines(models.Model):
    _name = 'project.contract.stage.line'

    name = fields.Char(compute='compute_name')

    @api.depends('contract_line_id', 'stage_id')
    def compute_name(self):
        for rec in self:
            rec.name = f'{rec.percent}% - {rec.item.name if rec.item else ""} - {rec.description}'

    contract_line_id = fields.Many2one('project.contract.line', required=True, ondelete='cascade')
    code = fields.Char(related='contract_line_id.code')
    item = fields.Many2one(related='contract_line_id.item', store=True)
    item_line = fields.Many2one(related='contract_line_id.item_line', store=True)

    description = fields.Char(related='contract_line_id.name', store=True)

    related_job_id = fields.Many2one(related='contract_line_id.related_job_id')
    qty = fields.Float(related='contract_line_id.qty')
    price_unit = fields.Float(store=True)

    stage_id = fields.Many2one("contract.stage.line", required=True)
    percent = fields.Float(related='stage_id.prec')

    contract_id = fields.Many2one(related='contract_line_id.contract_id', store=True)


# العقد
class ContractLines(models.Model):
    _name = 'project.contract.line'

    def create_stage_lines(self):

        for rec in self:
            global_stages = rec.contract_id.stage_ids
            if not rec.stage_ids:
                rec.stage_ids = [(0, 0, {
                    'stage_id': stg.stage_id.id,
                    'prec': stg.prec,
                }) for stg in global_stages]

            if rec.display_type:
                continue
            res = self.env['project.contract.stage.line']
            for stage in rec.stage_ids:
                # print(rec, stage)
                res.create({
                    'contract_line_id': rec.id,
                    'stage_id': stage.id,
                    'price_unit': rec.price_unit * stage.prec / 100,
                })

    contract_id = fields.Many2one("project.contract")
    project_id = fields.Many2one("project.project", related="contract_id.project_id")
    name = fields.Char(required=True, string="Description")

    code = fields.Char()
    sequence = fields.Integer(string='Sequence', default=10)
    item = fields.Many2one("project.item")
    item_line = fields.Many2one("project.tender")
    desc_item = fields.Char(string="وصف بند المقاول")
    item_sub_id = fields.Many2one("project.item", string="بند المقاول")
    related_job_id = fields.Many2one("project.related.job")
    uom_id = fields.Many2one("uom.uom", related="item.uom_id")
    qty = fields.Float()

    price_unit = fields.Float()
    amount_subtotal = fields.Float(compute='_compute_subtotal_total')
    amount_total = fields.Float(compute='_compute_tax_amount')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False)
    tax_ids = fields.Many2many("account.tax", )
    amount_tax = fields.Float(compute='_compute_tax_amount')
    note = fields.Char()
    stage_ids = fields.One2many("contract.stage.line", "contract_line_id")
    state = fields.Selection(related='contract_id.state')
    subcontractor = fields.Many2one(related='contract_id.subcontractor', domain=[('supplier_rank', '!=', 0)])
    is_subcontract = fields.Boolean(related='contract_id.is_subcontract', )

    def add_stage(self):
        return {
            'name': 'Add Stage',
            'view_mode': 'form',
            'view_id': self.env.ref('contract.contract_stage_line_view_form').id,
            'res_model': 'project.contract.line',
            'res_id': self.id,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    @api.constrains('stage_ids')
    def _check_stage_ids(self):
        if sum(self.stage_ids.mapped('prec')) != 100 and self.stage_ids:
            raise ValidationError("Precentage stage must be 100")

    @api.depends('qty', 'price_unit')
    def _compute_subtotal_total(self):
        for rec in self:
            rec.amount_subtotal = rec.qty * rec.price_unit

    @api.depends('tax_ids', 'amount_subtotal')
    def _compute_tax_amount(self):
        for rec in self:
            rec.amount_tax = 0
            for tax in rec.tax_ids:
                rec.amount_tax += (tax.amount / 100) * rec.amount_subtotal
            rec.amount_total += rec.amount_subtotal + rec.amount_tax

    @api.onchange('item', 'subcontractor')
    def _onchnage_item(self):
        if not self.name and self.item:
            self.name = self.item.name
            self.related_job_id = self.item.related_job_id.id if self.item.related_job_id else ''
        # if self.subcontractor and self.contract_id.project_id and self.contract_id.partner_id:
        #     item_ids = self.env['project.contract.line'] \
        #         .search([ \
        #         ('contract_id.project_id', '=', self.contract_id.project_id.id),
        #         ('contract_id.partner_id', '=', self.contract_id.partner_id.id),
        #     ])
        #     return {'domain': {'item': [('id', 'in', item_ids.item.ids)]}}

    @api.onchange('item_sub_id')
    def _onchnage_item_sub_id(self):
        if not self.desc_item and self.item_sub_id:
            self.desc_item = self.item_sub_id.name

    def action_draft(self):
        self.state = 'draft'


class Deduction(models.Model):
    _name = "contract.deduction.lines"

    contract_id = fields.Many2one("project.contract")
    contract_type = fields.Selection([('owner', 'owner'), ('subconstructor', 'subconstructor')], default='owner',
                                     string="Type of Contract")
    name = fields.Many2one("contract.deduction.allowance",
                           domain="[('type','=',contract_type),('subtype','=','deduction')]")
    is_precentage = fields.Boolean()
    percentage = fields.Float()
    value = fields.Float()
    counterpart_account_id = fields.Many2one("account.account", related='name.counterpart_account_id')
    amount_total_contract = fields.Float(related='contract_id.amount_total')

    @api.onchange('contract_id', 'amount_total_contract', 'percentage', 'is_precentage', 'name', 'value')
    def _onchange_is_precentage(self):
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        if self.name and self.percentage == 0:
            if self.name.calculation_type == 'percentage':
                self.percentage = self.name.amount
                self.is_precentage = True
            else:
                self.value = self.name.amount

        if self.is_precentage == True:

            self.value = self.amount_total_contract * (self.percentage / 100)
        else:

            self.percentage = self.value * 100 / (self.amount_total_contract) if self.value > 0 else 0


class Allownace(models.Model):
    _name = "contract.allowance.lines"

    contract_id = fields.Many2one("project.contract")
    contract_type = fields.Selection([('owner', 'owner'), ('subconstructor', 'subconstructor')], default='owner',
                                     string="Type of Contract")
    name = fields.Many2one("contract.deduction.allowance", domain="[('type','=',contract_type),\
    ('subtype','=','allowance')]")
    is_precentage = fields.Boolean()
    percentage = fields.Float()
    value = fields.Float()
    counterpart_account_id = fields.Many2one("account.account", related='name.counterpart_account_id')

    amount_total_contract = fields.Float(related='contract_id.amount_total')

    @api.onchange('contract_id', 'amount_total_contract', 'percentage', 'is_precentage', 'name', 'value')
    def _onchange_is_precentage(self):
        if self.name and self.percentage == 0:
            if self.name.calculation_type == 'percentage':
                self.percentage = self.name.amount
                self.is_precentage = True
            else:
                self.value = self.name.amount

        if self.is_precentage == True:

            self.value = self.amount_total_contract * (self.percentage / 100)
        else:
            self.percentage = self.value * 100 / (self.amount_total_contract) if self.value > 0 else 0
