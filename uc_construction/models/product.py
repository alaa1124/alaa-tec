from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Product(models.Model):
    _inherit='product.template'
    subcontracted = fields.Boolean(string="Subcontracted")
    uc_rent_ok = fields.Boolean(string="Can be Rented")
