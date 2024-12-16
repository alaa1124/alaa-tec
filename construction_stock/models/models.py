# -*- coding: utf-8 -*-

from odoo import models, fields, api


class construction_stock(models.Model):
    _inherit = "stock.picking"
    project_id = fields.Many2one("project.project")


class StockMove(models.Model):
    _inherit = "stock.move"
    project_id = fields.Many2one('project.project', related='picking_id.project_id')
    item_id = fields.Many2one("project.item", domain="[('id','in',allowed_item_ids)]")
    item_line = fields.Many2one('project.tender', domain="[('project_id','=?',project_id), ('item','=?',item_id)]")
    allowed_item_ids = fields.Many2many("project.item", "stock_move_item", "item", "id", compute="get_allowed_item_ids")

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
