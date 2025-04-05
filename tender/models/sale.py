from odoo import models, fields, api


class SalesOrder(models.Model):
    _name = "construction.sale.order"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    name = fields.Char("name")
    project_id = fields.Many2one("project.project", string="Project")
    tag_ids = fields.Many2many('project.tags', relation='construction_sale_order_project_tags_rel',
                               related='project_id.tag_ids', string='Tags')
    partner_id = fields.Many2one("res.partner", string="Customer")
    created_date = fields.Date("Created Date")
    order_lines = fields.One2many("construction.sale.order.line", "sale_id")
    discount_lines = fields.Float("Discount")
    amount_before_dis = fields.Float(compute='_get_total_amount_dis', string="Total Amount")
    total_discount = fields.Float(compute="_get_total_amount_dis", string="Total Discount")
    total = fields.Float(compute="_get_total_value", string="Total")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),('cancel','Cancel')], default="draft")
    active = fields.Boolean(default=True)
    version = fields.Char()
    version_num = fields.Integer()
    estimation_version = fields.Char()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    amount_tax = fields.Float(compute="get_amount_tax")
    tag_id_custom = fields.Char(string='Tags', compute='_get_tags', store=True)
    global_discount = fields.Float("Discount%")

    def action_cancel(self):
        self.state='cancel'


    @api.model
    @api.depends('tag_ids')
    def _get_tags(self):
        tag_custom = ''
        for rec in self:
            if rec.tag_ids:

                tag_custom = ','.join([p.name for p in rec.tag_ids])
            else:
                tag_id_custom = ''
            rec.tag_id_custom = tag_custom

    @api.depends( 'order_lines.tax_ids','order_lines')
    def get_amount_tax(self):
        for rec in self:
            rec.amount_tax = 0
            for line in rec.order_lines:
                for tax in line.tax_ids:
                    rec.amount_tax+= line.price_unit * (tax.amount / 100)

    def action_round(self):
        for rec in self.order_lines:
            rec.price_unit = round(rec.price_unit)

    @api.onchange("discount_lines")
    def _onchnage_discount(self):
        for rec in self.order_lines:
            rec.discount = self.discount_lines

    def action_confirm(self):
        self.state = "confirm"
        sales_id = self.search([('project_id','=',self.project_id.id),('id','!=',self.id),('active','in',(False,True))])
        print("==========",sales_id)
        for rec in sales_id:
            rec.action_cancel()

    @api.onchange("global_discount")
    @api.depends("order_lines", "order_lines.total_value")
    def _get_total_amount_dis(self):
        for record in self:
            record.amount_before_dis = 0
            record.total_discount = 0
            amount_before_dis, total_discount = 0, 0
            for rec in record.order_lines:
                amount_before_dis += (rec.price_unit)
                # total_discount += (rec.price_unit * rec.qty) - rec.total_value
            if record.global_discount:
                total_discount = amount_before_dis * (record.global_discount/100)

            record.amount_before_dis = amount_before_dis
            record.total_discount = total_discount

    @api.depends("amount_before_dis","total_discount", "discount_lines", "amount_tax")
    def _get_total_value(self):
        for record in self:
            record.total = record.amount_before_dis - record.total_discount - record.discount_lines + record.amount_tax


class SalesOrderLine(models.Model):
    _name = "construction.sale.order.line"
    name = fields.Char("Code")
    sale_id = fields.Many2one("construction.sale.order")
    item = fields.Many2one('project.item', string='Item')
    description = fields.Char("Description")
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")
    qty = fields.Float("Quantity")
    notes = fields.Char("Notes")
    price_unit = fields.Float("Sales Price ")
    discount = fields.Float("Discount % ", )
    total_value = fields.Float("Total value ")
    type = fields.Selection([('main', 'View'), ('transcation', 'Transcation')], string='Type', default='main')
    tender_id = fields.Many2one('project.tender', string="Tender ID")
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    sequence = fields.Integer(string='Sequence', default=10)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    price = fields.Float("Price Unit", compute='get_price')
    tax_ids = fields.Many2many(
        comodel_name='account.tax',
        string='taxes',domain="[('type_tax_use','=','sale')]")
    amount_after_tax = fields.Float(compute="get_amount_after_tax")
    amount_tax = fields.Float(compute="get_amount_after_tax")

    @api.depends('price_unit','tax_ids')
    def get_amount_after_tax(self):
        for rec in self:
            amount_tax = 0
            for tax in rec.tax_ids:
                amount_tax+=round((tax.amount/100)*rec.price_unit)
            rec.amount_after_tax=rec.price_unit+amount_tax
            rec.amount_tax=amount_tax

    @api.depends('price_unit', 'qty')
    def get_price(self):
        for rec in self:
            if rec.qty > 0:
                rec.price = rec.price_unit / rec.qty
            else:
                rec.price = 0

    # @api.depends("price_unit", "qty","discount")
    # def _get_total_value(self):
    #     for rec in self:
    #         value =rec.price_unit * rec.qty
    #         rec.total_value = (value)-(value*(rec.discount/100))
