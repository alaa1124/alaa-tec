from odoo import fields, models, api


class Labour(models.Model):
    _name = 'construction.labour'
    _description = 'Labour'
    name = fields.Char()
    job_id = fields.Many2one("construction.job.cost",ondelete='cascade')
    product_id = fields.Many2one("product.product", domain="[('labour','=',True)]")
    uom_id = fields.Many2one("uom.uom")
    qty = fields.Float(default=1)
    price_unit = fields.Float()
    subtotal = fields.Float(compute='get_subtotal')
    total_qty = fields.Float(compute='compute_total_qty', string='Total Quantity')
    total_cost = fields.Float(compute='compute_total_cost', string='Total Value')

    @api.depends('job_id', 'subtotal')
    def compute_total_cost(self):
        for rec in self:
            rec.total_cost = 0
            rec.total_cost = rec.subtotal *  rec.job_id.qty

    @api.depends('qty', 'total_qty')
    def compute_total_qty(self):
        for rec in self:
            rec.total_qty = 0
            if rec.job_id:
                rec.total_qty = rec.qty *  rec.job_id.qty

    @api.onchange('product_id')
    def _onchange_product(self):
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id
            self.name = self.product_id.name
            self.price_unit = self.product_id.lst_price
            return {
                'domain': {'uom_id': [('category_id', '=', self.product_id.uom_id.id)]}
            }

    @api.depends('price_unit', 'qty')
    def get_subtotal(self):
        for rec in self:
            rec.subtotal = rec.qty * rec.price_unit

