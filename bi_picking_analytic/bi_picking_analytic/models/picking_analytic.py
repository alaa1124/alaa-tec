# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.tools.float_utils import float_is_zero, float_compare
from datetime import datetime


class ProcurementRule(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id,
                               values):
        result = super(ProcurementRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id,
                                                                     name, origin, company_id, values)

        result.update({
            'analytic_account_id': values.get('analytic_account_id', 0),
            'tag_ids': values.get('tag_ids', 0),

        })
        return result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_procurement_values(self, group_id):
        res = super(SaleOrderLine, self)._prepare_procurement_values(group_id=group_id)
        tag_ids = []
        for tag in self.analytic_tag_ids:
            tag_ids.append(tag.id)
        res.update({
            'analytic_account_id': self.order_id.analytic_account_id.id,
            'tag_ids': [(6, 0, tag_ids)],

        })
        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        self.ensure_one()
        self._check_orderpoint_picking_type()
        product = self.product_id.with_context(lang=self.order_id.dest_address_id.lang or self.env.user.lang)
        date_planned = self.date_planned or self.order_id.date_planned
        tag_ids = []
        for tag in self.analytic_tag_ids:
            tag_ids.append(tag.id)
        return {
            # truncate to 2000 to avoid triggering index limit error
            # TODO: remove index in master?
            'name': (self.name or '')[:2000],
            'product_id': self.product_id.id,
            'date': date_planned,
            'date_deadline': date_planned,
            'location_id': self.order_id.partner_id.property_stock_supplier.id,
            'location_dest_id': (self.orderpoint_id and not (
                        self.move_ids | self.move_dest_ids)) and self.orderpoint_id.location_id.id or self.order_id._get_destination_location(),
            'picking_id': picking.id,
            'partner_id': self.order_id.dest_address_id.id,
            'move_dest_ids': [(4, x) for x in self.move_dest_ids.ids],
            'state': 'draft',
            'analytic_account_id': self.account_analytic_id.id,
            'tag_ids': [(6, 0, tag_ids)],
            'purchase_line_id': self.id,
            'company_id': self.order_id.company_id.id,
            'price_unit': price_unit,
            'picking_type_id': self.order_id.picking_type_id.id,
            'group_id': self.order_id.group_id.id,
            'origin': self.order_id.name,
            'description_picking': product.description_pickingin or self.name,
            'propagate_cancel': self.propagate_cancel,
            'warehouse_id': self.order_id.picking_type_id.warehouse_id.id,
            'product_uom_qty': product_uom_qty,
            'product_uom': product_uom.id,
            'product_packaging_id': self.product_packaging_id.id,
        }


class StockMove(models.Model):
    _inherit = "stock.move"

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    tag_ids = fields.Many2many('account.analytic.tag', string='Tag')

    def _prepare_account_move_vals(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id,
                                   cost):
    # def _prepare_account_move_line(self, qty, cost,
    #                                credit_account_id, debit_account_id,description):

        self.ensure_one()
        res = super(StockMove, self)._prepare_account_move_line(credit_account_id, debit_account_id, journal_id, qty, description, svl_id,
                                   cost)
        # Add analytic account in debit line
        if not self.analytic_account_id:
            return res

        for num in range(0, 2):
            if res[num][2]["account_id"] != self.product_id. \
                    categ_id.property_stock_valuation_account_id.id:
                res[num][2].update({
                    'analytic_account_id': self.analytic_account_id.id,

                })
        return res


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        sale_list = []
        ref = self.name
        sale_analytic_dict = {}
        purchase_analytic_dict = {}
        if self.sale_id:
            for line in self.move_ids_without_package:
                if line.analytic_account_id:
                    tag_ids = []
                    for tag_id in line.tag_ids:
                        tag_ids.append(tag_id.id)
                    sale_analytic_dict.update({
                        'name': line.sale_line_id.product_id.name,
                        'amount': line.sale_line_id.price_unit,
                        'product_id': line.sale_line_id.product_id.id,
                        'product_uom_id': line.sale_line_id.product_uom.id,
                        'date': line.date,
                        'account_id': line.analytic_account_id.id,
                        'unit_amount': line.quantity_done,
                        'general_account_id': self.partner_id.property_account_receivable_id.id,
                        'ref': ref,
                        'group_id': line.analytic_account_id.group_id.id,
                        'tag_ids': [(6, 0, tag_ids)]
                    })
                    print("------------jjgj-------------", sale_analytic_dict)

                    self.env['account.analytic.line'].create(sale_analytic_dict)

        if self.purchase_id:
            for line in self.move_ids_without_package:
                if line.analytic_account_id:
                    tag_ids = []
                    for tag_id in line.tag_ids:
                        tag_ids.append(tag_id.id)

                    purchase_analytic_dict.update({
                        'name': line.purchase_line_id.product_id.name,
                        'date': line.date,
                        'account_id': line.analytic_account_id.id,
                        'unit_amount': line.quantity_done,
                        'amount': (line.product_id.standard_price * line.quantity_done) * -1,
                        'product_id': line.purchase_line_id.product_id.id,
                        'product_uom_id': line.purchase_line_id.product_uom.id,
                        'general_account_id': self.partner_id.property_account_payable_id.id,
                        'group_id': line.analytic_account_id.group_id.id,
                        'ref': ref,
                        'tag_ids': [(6, 0, tag_ids)]
                    })

                    self.env['account.analytic.line'].create(purchase_analytic_dict)
                    print("---------------------", purchase_analytic_dict)

        if not self.purchase_id and not self.sale_id:
            for line in self.move_ids_without_package:
                if line.analytic_account_id:
                    tag_ids = []
                    for tag_id in line.tag_ids:
                        tag_ids.append(tag_id.id)

                    purchase_analytic_dict.update({

                        'name': line.product_id.name,
                        'date': datetime.now(),
                        'account_id': line.analytic_account_id.id,
                        'unit_amount': line.quantity_done,
                        'amount': line.product_id.lst_price * line.quantity_done,
                        'product_id': line.product_id.id,
                        'product_uom_id': line.product_uom.id,
                        'general_account_id': self.partner_id.property_account_receivable_id.id,
                        'ref': ref,
                        'tag_ids': [(6, 0, tag_ids)]
                    })
                    if self.picking_type_id.code == 'incoming':
                        purchase_analytic_dict['amount'] = (line.product_id.standard_price * line.quantity_done) * -1

                    self.env['account.analytic.line'].create(purchase_analytic_dict)
        return super(StockPicking, self).button_validate()



# class StockInventoryLine(models.Model):
#     _inherit = "stock.inventory.line"
#
#
#
#     analytic_account_id = fields.Many2one(
#         "account.analytic.account",
#         string="Analytic Account",relation="inventory_analytic",
#     )
#     tag_ids = fields.Many2many(
#         "account.analytic.tag",
#         string="Analytic Tags",relation="inventory_analytic_tags",
#     )
#
#     def _get_move_values(self, qty, location_id, location_dest_id, out):
#         res = super(StockInventoryLine, self)._get_move_values(
#             qty, location_id, location_dest_id, out
#         )
#         if self.analytic_account_id:
#             res["analytic_account_id"] = self.analytic_account_id.id
#         if self.tag_ids:
#             res["tag_ids"] = [(6, 0, self.tag_ids.ids)]
#         return res
