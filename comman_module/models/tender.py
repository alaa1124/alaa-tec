from odoo import fields, models, api


class Tender(models.Model):
    _name = 'project.tender'
    _description = 'Tender'
    state = fields.Selection([('main', 'Main'), ('job_cost', 'Break Down'), \
                              ('job_estimate', 'Break Down Estimate')],
                             string="State", default="main")
    project_id = fields.Many2one("project.project")
    name = fields.Char(required=True, string="Description")
    code = fields.Char( )
    sequence = fields.Integer(string='Sequence', default=10)
    item = fields.Many2one("project.item")
    related_job_id = fields.Many2one("project.related.job")
    uom_id = fields.Many2one("uom.uom", related="item.uom_id")
    qty = fields.Float(default=1)

    price_unit = fields.Float(compute='_compute_sale_price')
    cost_unit = fields.Float(compute='get_cost_unit')
    total_direct = fields.Float( )
    total_indirect = fields.Float()
    total_profit = fields.Float()
    sale_price = fields.Float(compute='_compute_sale_price')
    amount_total = fields.Float(compute='_compute_amount_total')
    profit = fields.Float()
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    tax_ids = fields.Many2many("account.tax")
    amount_tax = fields.Float(compute='_compute_tax_amount',domain="[('type_tax_use','=','sale')]")
    note = fields.Char()

    @api.depends('qty', 'total_direct', 'total_indirect')
    def get_cost_unit(self):
        for rec in self:
            rec.cost_unit = (rec.total_direct + rec.total_indirect) / rec.qty if rec.qty > 0 else 0

    @api.depends('amount_tax', 'sale_price')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = rec.sale_price + rec.amount_tax

    @api.depends('tax_ids', 'sale_price')
    def _compute_tax_amount(self):
        for rec in self:
            rec.amount_tax = 0
            for tax in rec.tax_ids:
                rec.amount_tax += (tax.amount / 100) * rec.sale_price

    @api.depends('total_direct', 'total_indirect', 'total_profit','qty')
    def _compute_sale_price(self):
        for rec in self:
            rec.sale_price = rec.total_direct + rec.total_indirect + rec.total_profit
            rec.price_unit = rec.sale_price / rec.qty if rec.qty > 0 else 0

    # @api.depends("price_unit", "qty")
    # def _get_total_value(self):
    #     for rec in self:
    #         rec.total_direct = 0
    #         if rec.id:
    #             job_ids = self.env['construction.job.cost'].search([('state','!=','draft'),('tender_id','=',rec.id)])




    @api.onchange('item')
    def _onchnage_item(self):
        if not self.name and self.item:
            self.name = self.item.name
            self.related_job_id = self.item.related_job_id.id if self.item.related_job_id else ''
