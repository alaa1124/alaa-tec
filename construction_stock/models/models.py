# -*- coding: utf-8 -*-

from odoo import models, fields, api


class construction_stock(models.Model):
    _inherit = "stock.picking"
    project_id = fields.Many2one("project.project")


class StockMove(models.Model):
    _inherit = "stock.move"
    project_id = fields.Many2one('project.project', related='picking_id.project_id')
    item_id = fields.Many2one("project.item", domain="[('id','in',allowed_item_ids)]")
    item_line = fields.Many2one('project.tender', domain="[('project_id','=',project_id), ('item','=',item_id)]")
    allowed_item_ids = fields.Many2many("project.item", "stock_move_item", "item", "id", compute="get_allowed_item_ids")

    analytic_distribution = fields.Json(related='purchase_line_id.analytic_distribution')
    analytic_precision = fields.Integer(related='purchase_line_id.analytic_precision')

    @api.depends('picking_id.project_id')
    def get_allowed_item_ids(self):
        for rec in self:
            rec.allowed_item_ids = []
            if rec.picking_id.project_id:
                items_ids = self.env['project.tender'].sudo().search(
                    [('project_id', '=', rec.picking_id.project_id.id)])
                print(">>>>>>>>>>>>>>>.", items_ids)
                for item in items_ids:
                    rec.allowed_item_ids = [(4, item.item.id)]

    @api.onchange('item_id')
    def onchange_item_id(self):
        self.item_line = None


class stockvaluationlayer(models.Model):
    _inherit = 'stock.valuation.layer'

    item_id = fields.Many2one(related='stock_move_id.item_id', store=True)
    item_line = fields.Many2one(related='stock_move_id.item_line', store=True)

    @api.constrains('item_id', 'item_line')
    def set_item_on_aml(self):
        for rec in self:
            if rec.item_id and rec.item_line:
                rec.account_move_id.line_ids.write({
                    'item': rec.item_id.id,
                    'item_line': rec.item_line.id,
                })
