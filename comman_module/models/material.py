from odoo import fields, models, api


class Material(models.Model):
    _name = 'construction.material'
    _description = 'Material'

    name = fields.Char()
    job_id = fields.Many2one("construction.job.cost", ondelete='cascade')
    product_id = fields.Many2one("product.product", domain="[('material','=',True)]")
    uom_id = fields.Many2one("uom.uom")

    def _default_currency_id(self):
        return self.env.user.company_id.currency_id

    currancy_id = fields.Many2one("res.currency", default=lambda self: self._default_currency_id())

    ratio = fields.Float(default=1)
    qty = fields.Float(default=1)
    waste = fields.Float()
    planned_qty = fields.Float(compute='get_planned_qty')
    price_unit = fields.Float()
    subtotal = fields.Float(compute='get_subtotal')
    total_qty = fields.Float(compute='compute_total_qty', string='Total Quantity')
    total_cost = fields.Float(compute='compute_total_cost', string='Total Value')
    total_qty_as_total = fields.Float()

    @api.onchange('total_qty_as_total','job_id')
    def _onchange_total_qty_as_total(self):
        if self.total_qty_as_total > 0 and self.job_id:
            if self.job_id.qty:
                self.qty = self.total_qty_as_total/self.job_id.qty

    @api.onchange('currancy_id')
    def onchange_currancy_id(self):
        if self.currancy_id and self.job_id.project_id:
            # if self.job_id.job_template:
            #     self.ratio = self.job_id.job_template.currancy_id if self.job_id.job_template.currancy_id else 1

            if self.job_id.project_id.currency_ids:
                if self.job_id.project_id.currency_ids.search([('currency_id', '=', self.currancy_id.id)], limit=1):
                    currancy_id = self.env['project.currency'] \
                        .search(
                        [('currency_id', '=', self.currancy_id.id), ('project_id', '=', self.job_id.project_id.id)])
                    self.ratio = currancy_id.rate if currancy_id else 1

    @api.depends('job_id', 'subtotal')
    def compute_total_cost(self):
        for rec in self:
            rec.total_cost = 0
            rec.total_cost = rec.subtotal * rec.job_id.qty

    @api.depends('planned_qty', 'total_qty')
    def compute_total_qty(self):
        for rec in self:
            rec.total_qty = 0
            if rec.job_id:
                rec.total_qty = rec.planned_qty * rec.job_id.qty

    @api.onchange('product_id')
    def _onchange_product(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id
            self.name = self.product_id.name
            self.price_unit = self.product_id.lst_price
            return {
                'domain': {'uom_id': [('category_id', '=', self.product_id.uom_id.id)]}
            }

    @api.depends('price_unit', 'planned_qty', 'ratio')
    def get_subtotal(self):
        for rec in self:
            rec.subtotal = rec.planned_qty * rec.price_unit * rec.ratio

    @api.depends('waste', 'qty')
    def get_planned_qty(self):
        for rec in self:
            rec.planned_qty = ((rec.waste / 100) * rec.qty) + rec.qty
