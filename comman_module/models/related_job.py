from odoo import fields, models, api


class related_job(models.Model):
    _name = 'project.related.job'
    _description = 'Related Job'

    name = fields.Char(required=True)
    code = fields.Char(required=True)
