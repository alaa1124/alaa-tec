# -*- coding: utf-8 -*-

from odoo import models, fields, api


class purchase_template(models.Model):
    _inherit = 'purchase.order'
    project_note = fields.Text("Note")
    project_label = fields.Char("Label")
    project_name = fields.Many2one("account.analytic.account")
