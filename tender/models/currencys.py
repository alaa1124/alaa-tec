from odoo import fields, models, api


class Currency(models.Model):
    _name = 'project.currency'
    currency_id = fields.Many2one("res.currency")
    rate = fields.Float(default=1)
    project_id = fields.Many2one("project.project")
