from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    hide_peppol_fields = fields.Boolean()
    is_coa_installed = fields.Boolean()