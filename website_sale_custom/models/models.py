# -*- coding: utf-8 -*-

from odoo import models, fields, api
from num2words import num2words


class ProductTemplate(models.Model):
    _inherit = 'res.company'

    form_file = fields.Binary()
    form_file_name = fields.Char(string='Form File Name')

    terms_and_conditions = fields.Html()


class OwnershipContract(models.Model):
    _inherit = "ownership.contract"

    sale_order_line = fields.Many2one('sale.order.line', ondelete='cascade')
    sale_order = fields.Many2one(related='sale_order_line.order_id')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    reservation = fields.One2many('ownership.contract', 'sale_order_line')

    def create_reservation(self):
        order = self.order_id
        self.reservation.create({
            'sale_order_line': self.id,
            'partner_id': order.partner_id.id,
            'building_unit': self.product_template_id.id,
            'date_payment': order.date_order.date()
        })

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res.order_id.website_id:
            res.create_reservation()

        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _cart_update_order_line(self, *args, **kwargs):
        order = super()._cart_update_order_line(*args, **kwargs)
        order.write({
            'product_uom_qty': 1
        })
        return order