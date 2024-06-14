from odoo import fields, models, api
from odoo.exceptions import ValidationError

class topSheet(models.Model):
    _name = 'top.sheet'
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']
    _description = 'Top Sheet'
    project_id = fields.Many2one("project.project")
    total_cost = fields.Float(related='project_id.total_direct_indirect')
    split_method = fields.Selection([('equal','Equal'),('cost','Cost')],default='equal')
    line_ids = fields.One2many("top.sheet.lines","parent_id")
    state = fields.Selection([('draft','Draft'),('confirm','Confirm'),('cancel','Cancel')],default='draft')

    total = fields.Float(compute='get_total')

    @api.depends('line_ids')
    def get_total(self):
        for rec in self:
            rec.total = 0
            if rec.line_ids:
                rec.total = sum(rec.line_ids.mapped('price'))

    @api.constrains('project_id')
    def get_projects(self):
        project_id = self.env['top.sheet'].search([('project_id', '=', self.project_id.id) \
                                                          , ('state', '!=', 'cancel')])
        if len(project_id) > 1:
            raise ValidationError("direct Cost must be unique bar project")

    def action_confirm(self):
        self.state = 'confirm'
        value = self.refersh_cost()
        if self.split_method == 'equal':
            for rec in self.project_id.tender_ids:
                if rec.display_type == False:
                    rec.total_profit = value
        if self.split_method == 'cost':
            total_profit_cost = sum(self.line_ids.mapped('price'))
            for rec in self.project_id.tender_ids:
                if rec.display_type == False:
                    rec.total_profit = (((rec.total_direct+rec.total_indirect) / self.project_id.total_direct_indirect)) * total_profit_cost
        self.project_id.profit_id = self.id

    def set_draft(self):
        self.state = 'draft'

    def action_cancel(self):
        self.state = 'cancel'
        for rec in self.project_id.tender_ids:
            if rec.display_type == False:
                rec.total_profit = 0

    # split_method = fields.Selection([('equal', 'Equal'), ('qty', 'Quantity'), ('cost', 'Cost')], default='equal')

    def refersh_cost(self):
        if self.split_method == 'equal':
            cost = 0
            total_profit_cost = sum(self.line_ids.mapped('price'))
            return total_profit_cost / len(
                self.project_id.tender_ids.filtered(lambda line: line.display_type == False))

        if self.split_method == 'cost':
            total_value = 0
            total_value = sum(self.project_id.tender_ids.mapped('total_direct'))+ sum(self.project_id.tender_ids.mapped('total_indirect'))

            return total_value

class TopSheetLines(models.Model):
    _name = "top.sheet.lines"
    parent_id = fields.Many2one("top.sheet")
    product_id = fields.Many2one("product.product",domain="[('top_sheet','=',True)]")
    prec = fields.Float("Prec %")
    price = fields.Float("Price")

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


