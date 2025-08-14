# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class Stock(models.Model):
    _inherit = 'stock.picking'
    def button_validate(self):
        res=super(Stock, self).button_validate()
        for rec in self:
            if rec.purchase_id:
                rec.purchase_id.late_delivery=''
        return res
class tec_custom(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self,vals):
        res=super(tec_custom, self).create(vals)
        if not self.env.user.has_group('tec_custom.group_create_product'):
            raise ValidationError("You cann't Create Product")
        return res
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def create(self,vals):
        res=super(ProductTemplate, self).create(vals)
        if not self.env.user.has_group('tec_custom.group_create_product'):
            raise ValidationError("You cann't Create Product")
        return res