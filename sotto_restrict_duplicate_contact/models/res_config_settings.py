# -*- coding: utf-8 -*-

from odoo import models, fields


class Resconfigsetting(models.TransientModel):
    _inherit = "res.config.settings"

    stop_duplicate_contact = fields.Boolean(
        "Duplicate Contact alert", related="company_id.stop_duplicate_contact", readonly=False)
    duplicate_contact_fields = fields.Many2many('ir.model.fields',
                                                string="Contact Fields", related="company_id.duplicate_contact_fields", readonly=False)
