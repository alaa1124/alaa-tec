from odoo import fields, models, api


class Item(models.Model):
    _name = 'project.item'
    _description = 'Item'

    name = fields.Char(required=True)
    related_job_id = fields.Many2one("project.related.job")
    uom_id = fields.Many2one("uom.uom",string="unit of measure",required=True)

    item_lines = fields.One2many('project.tender', 'item')
