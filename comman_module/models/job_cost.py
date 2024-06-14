

from datetime import datetime

from odoo import fields, models, api
class Projects(models.Model):
    _inherit = "project.project"

    state = fields.Selection([('draft', 'draft'), ('confirm', 'confirm')], default='draft')


class JobCost(models.Model):
    _name = "construction.job.cost"
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    code = fields.Char()
    item_id = fields.Many2one("project.item")
    related_job_id = fields.Many2one("project.related.job")
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")
    description = fields.Char(string="Description")
    name = fields.Char(string="Name", compute='get_name')
    unit_type = fields.Selection([('unit', 'unit'), ('total', 'Total')], default='unit')
    is_template = fields.Boolean()
    qty = fields.Float(default=1)
    material_ids = fields.One2many("construction.material", "job_id")
    labour_ids = fields.One2many("construction.labour", "job_id")
    expense_ids = fields.One2many("construction.expense", "job_id")
    subconstractor_ids = fields.One2many("construction.subconstractor", "job_id")
    equipment_ids = fields.One2many("construction.equipment", "job_id")

    total_material = fields.Float(compute='_compute_cost_per_unit')
    total_labour = fields.Float(compute='_compute_cost_per_unit')
    total_expense = fields.Float(compute='_compute_cost_per_unit')
    total_subconstractor = fields.Float(compute='_compute_cost_per_unit')
    total_equipment = fields.Float(compute='_compute_cost_per_unit')
    total_value_all = fields.Float(compute='_compute_cost_per_unit')

    total_material_with_qty = fields.Float(compute='_compute_cost_per_unit_with_qty')
    total_labour_with_qty = fields.Float(compute='_compute_cost_per_unit_with_qty')
    total_expense_with_qty = fields.Float(compute='_compute_cost_per_unit_with_qty')
    total_subcontractor_with_qty = fields.Float(compute='_compute_cost_per_unit_with_qty')
    total_equipment_with_qty = fields.Float(compute='_compute_cost_per_unit_with_qty')
    total_value_all_with_qty = fields.Float(compute='_compute_cost_per_unit_with_qty')

    state = fields.Selection([('draft', 'draft'), ('confirm', 'Confirm'), ('approve', 'Approve'),
                              ('quotation', 'Financial Offer')], string="State", default="draft")
    techical_type = fields.Boolean()
    note = fields.Char()
    project_id = fields.Many2one('project.project')
    tender_id = fields.Many2one("project.tender")
    partner_id = fields.Many2one("res.partner")

    active = fields.Boolean(default=True)
    version_num = fields.Integer()
    version = fields.Char()
    start_date = fields.Date( )
    end_date = fields.Date( )
    dif = fields.Char(compute='get_differance')
    template_id = fields.Many2one("construction.job.cost", string="Break Down Template",
                                  domain="[('is_template','=',True)]")
    actual_qty = fields.Float()
    previous_qty = fields.Float()

    # @api.onchange('template_id', 'start_date')
    def write(self, vals):
        res = super(JobCost, self).write(vals)

        values = []
        if 'template_id' in vals:
            print("=========================",vals)
            for rec in self.template_id:
                if rec.material_ids:
                    for mat in rec.material_ids:
                        values.append((0, 0, {
                            'product_id': mat.product_id.id,
                            'name': mat.name,
                            'uom_id': mat.uom_id.id, 'qty': mat.qty,
                            'waste': mat.waste, 'price_unit': mat.price_unit,
                            'job_id':rec.id,

                        }))

                    self.material_ids = values
                if rec.labour_ids:
                    values = []

                    for lab in rec.labour_ids:
                        values.append((0, 0, {
                            'product_id': lab.product_id.id,
                            'name': lab.name,
                            'uom_id': lab.uom_id.id, 'qty': lab.qty,
                            'price_unit': lab.price_unit,
                            'job_id':rec.id,

                        }))
                    self.labour_ids = values

                if rec.expense_ids:
                    values = []

                    for exp in rec.expense_ids:
                        values.append((0, 0, {
                            'product_id': exp.product_id.id,
                            'name': exp.name,
                            'uom_id': exp.uom_id.id, 'qty': exp.qty,
                            'price_unit': exp.price_unit,
                            'job_id':rec.id,

                        }))
                    self.expense_ids = values
                if rec.subconstractor_ids:
                    values = []
                    for sub in rec.subconstractor_ids:
                        values.append((0, 0, {
                            'product_id': sub.product_id.id,
                            'name': sub.name,
                            'uom_id': sub.uom_id.id, 'qty': sub.qty,
                            'price_unit': sub.price_unit,
                            'job_id':rec.id,

                        }))
                    self.subconstractor_ids = values
                if rec.equipment_ids:
                    values = []
                    for equip in rec.equipment_ids:
                        values.append((0, 0, {
                            'product_id': sub.product_id.id,
                            'name': sub.name,
                            'uom_id': sub.uom_id.id, 'qty': sub.qty,
                            'price_unit': sub.price_unit,
                            'job_id':rec.id,

                        }))
                    self.equipment_ids = values
        return res

    @api.depends('start_date', 'end_date')
    def get_differance(self):
        for rec in self:
            rec.dif = ''
            if rec.start_date and rec.end_date:
                rec.dif = rec.end_date - rec.start_date

    def _default_currency_id(self):
        return self.env.user.company_id.currency_id

    currancy_id = fields.Many2one("res.currency", default=lambda self: self._default_currency_id())

    def action_confirm(self):
        self.state = 'confirm'


    def action_approve(self):
        self.state = 'approve'
        self.tender_id.total_direct = self.total_value_all_with_qty

    def action_quotation(self):
        self.state = 'quotation'

    @api.depends('project_id', 'code', 'description')
    def get_name(self):
        for rec in self:
            rec.name = ""
            if rec.project_id:
                rec.name += rec.project_id.name
            if rec.code:
                rec.name += rec.code
            if rec.description:
                rec.name += rec.description

    @api.depends('material_ids', 'labour_ids', 'equipment_ids', 'subconstractor_ids', 'expense_ids')
    def _compute_cost_per_unit(self):
        for rec in self:
            rec.total_material = rec.total_labour \
                = rec.total_expense = rec.total_subconstractor = rec.total_equipment = 0
            for line in rec.material_ids:
                rec.total_material += line.subtotal
            for line in rec.labour_ids:
                rec.total_labour += line.subtotal
            for line in rec.equipment_ids:
                rec.total_equipment += line.subtotal
            for line in rec.subconstractor_ids:
                rec.total_subconstractor += line.subtotal
            for line in rec.expense_ids:
                rec.total_expense += line.subtotal
            rec.total_value_all = rec.total_material + rec.total_expense + rec.total_labour + rec.total_subconstractor + rec.total_equipment

    @api.depends('material_ids', 'labour_ids', 'equipment_ids', 'subconstractor_ids', 'expense_ids')
    def _compute_cost_per_unit_with_qty(self):
        for rec in self:
            rec.total_material_with_qty = rec.total_labour_with_qty \
                = rec.total_expense_with_qty = rec.total_subcontractor_with_qty \
                = rec.total_equipment_with_qty = 0
            for line in rec.material_ids:
                rec.total_material_with_qty += line.total_cost
            for line in rec.labour_ids:
                rec.total_labour_with_qty += line.total_cost
            for line in rec.equipment_ids:
                rec.total_equipment_with_qty += line.total_cost
            for line in rec.subconstractor_ids:
                rec.total_subcontractor_with_qty += line.total_cost
            for line in rec.expense_ids:
                rec.total_expense_with_qty += line.total_cost
            rec.total_value_all_with_qty = rec.total_material_with_qty + rec.total_expense_with_qty \
                                           + rec.total_labour_with_qty + rec.total_subcontractor_with_qty \
                                           + rec.total_equipment_with_qty
