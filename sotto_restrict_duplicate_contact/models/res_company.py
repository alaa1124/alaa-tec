# -*- coding: utf-8 -*-

from odoo import models, fields


class Resconfigsetting(models.Model):
    _inherit = "res.company"

    stop_duplicate_contact = fields.Boolean("Duplicate Contact alert")
    duplicate_contact_fields = fields.Many2many('ir.model.fields',
                                                string="Contact Fields", domain="[('model','=','res.partner'),('store','=',True),('ttype','=','char')]")
