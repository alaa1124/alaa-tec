# -*- coding: utf-8 -*-

from odoo import models, fields, api
from num2words import num2words
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = 'res.company'

    form_file = fields.Binary()
    form_file_name = fields.Char(string='Form File Name')

    terms_and_conditions = fields.Html()


class OwnershipContract(models.Model):
    _name = "ownership.contract"
    _inherit = "ownership.contract"

    sale_order_line = fields.Many2one('sale.order.line', ondelete='cascade')
    sale_order = fields.Many2one(related='sale_order_line.order_id')
    documents = fields.Many2many('ir.attachment', relation='ownership_att_rel')

    attachment_ids = fields.One2many('ir.attachment', 'res_id',
                                     domain=[('res_model', '=', _name)], string='Attachments')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    active = fields.Boolean(default=True)

    reservation = fields.One2many('ownership.contract', 'sale_order_line')

    def create_reservation(self):
        order = self.order_id
        r = self.reservation.create({
            'sale_order_line': self.id,
            'partner_id': order.partner_id.id,
            'building_unit': self.product_template_id.id,
            'date_payment': order.date_order.date()
        })

        # print(order.attachment_ids)
        #
        # order.attachment_ids.write({
        #     'res_id': r.id,
        #     'res_model': r._name,
        # })

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res.order_id.website_id:
            res.create_reservation()

        return res


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    @api.depends('order_line.product_uom_qty', 'order_line.product_id')
    def _compute_cart_info(self):
        for order in self:
            order.cart_quantity = int(sum(order.mapped('website_order_line.product_uom_qty')))
            if order.cart_quantity > 1:
                raise UserError('Please finish the pending order first')
            order.only_services = all(l.product_id.type == 'service' for l in order.website_order_line)

    active = fields.Boolean(default=True)

    def send_attachment(self):
        r = self.order_line.reservation
        print(r)
        print(self.attachment_ids)
        if self.website_id and r:
            r.documents = [(6, 0, self.attachment_ids.ids)]
            self.attachment_ids.write({
                'res_id': r[0].id,
                'res_model': r._name,
            })

    def _cart_update_order_line(self, *args, **kwargs):
        order = super()._cart_update_order_line(*args, **kwargs)
        order.write({
            'product_uom_qty': 1
        })
        return order

    attachment_ids = fields.One2many('ir.attachment', 'res_id',
                                     domain=[('res_model', '=', _name)], string='Attachments')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    form_file = fields.Binary()
    form_file_name = fields.Char(string='Form File Name')

    terms_and_conditions = fields.Html()
