from odoo import fields, models, api

from odoo.exceptions import ValidationError
class IndirectCost(models.Model):
    _name = 'indirect.cost'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = 'Top Sheet'
    project_id = fields.Many2one("project.project")
    total_cost = fields.Float(related='project_id.total_direct_cost')
    split_method = fields.Selection([('equal', 'Equal'), ('cost', 'Cost')], default='equal')
    line_ids = fields.One2many("indirect.cost.lines", "parent_id")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('cancel', 'Cancel')], default='draft')
    total = fields.Float(compute='get_total')
    @api.depends('line_ids')
    def get_total(self):
        for rec in self:
            rec.total = 0
            if rec.line_ids:
                rec.total = sum(rec.line_ids.mapped('price'))

    @api.constrains('project_id')
    def get_projects(self):
        project_id = self.env['indirect.cost'].search([('project_id', '=', self.project_id.id) \
                                                          , ('state', '!=', 'cancel')])
        if len(project_id) > 1:
            raise ValidationError("direct Cost must be unique bar project")

    def action_confirm(self):
        self.state = 'confirm'
        value = self.refersh_cost()
        if self.split_method == 'equal':
            for rec in self.project_id.tender_ids:
                if rec.display_type == False:
                    rec.total_indirect = value
        if self.split_method == 'cost':
            total_indirect_cost = sum(self.line_ids.mapped('price'))
            for rec in self.project_id.tender_ids:
                if rec.display_type == False:
                    rec.total_indirect = ((rec.total_direct / self.project_id.total_direct_cost)) * total_indirect_cost
        self.project_id.indirect_id = self.id

    def set_draft(self):
        self.state = 'draft'

    def action_cancel(self):
        self.state = 'cancel'
        for rec in self.project_id.tender_ids:
            if rec.display_type == False:
                rec.total_indirect = 0

    # split_method = fields.Selection([('equal', 'Equal'), ('qty', 'Quantity'), ('cost', 'Cost')], default='equal')

    def refersh_cost(self):
        if self.split_method == 'equal':
            cost = 0
            total_indirect_cost = sum(self.line_ids.mapped('price'))
            return total_indirect_cost / len(
                self.project_id.tender_ids.filtered(lambda line: line.display_type == False))

        if self.split_method == 'cost':
            total_value = 0
            total_value = sum(self.project_id.tender_ids.mapped('total_direct'))

            return total_value

    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError("You cann't delete confirmed Indirect Cost")
        res = super(IndirectCost, self).unlink()

        return res


class IndirectCostLines(models.Model):
    _name = "indirect.cost.lines"
    parent_id = fields.Many2one("indirect.cost")
    product_id = fields.Many2one("product.product", domain="[('indirect_cost','=',True)]")
    prec = fields.Float("Prec %")
    price = fields.Float("Price")
    indirect_cost = fields.Float(related='parent_id.project_id.total_direct_cost')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.onchange('price')
    def onchange_price(self):
        if self.price > 0 and self.parent_id:
            self.prec = (self.price / self.parent_id.total_cost) * 100

    @api.onchange('prec')
    def onchange_prec(self):
        if self.prec > 0 and self.parent_id.total_cost > 0:

            other_price = (self.prec * self.parent_id.total_cost) / 100

            if other_price != self.price:
                self.price = (self.prec * self.parent_id.total_cost) / 100
