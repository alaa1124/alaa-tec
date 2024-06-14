from odoo import fields, models, api


class Products(models.Model):
    _inherit  = "product.template"
    expenses = fields.Boolean()
    material = fields.Boolean()
    labour = fields.Boolean()
    equipment = fields.Boolean()
    indirect_cost = fields.Boolean()
    subconstructor = fields.Boolean()
    top_sheet = fields.Boolean()
