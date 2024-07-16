from odoo import api, fields, models, _


class CrmLead(models.Model):
    _inherit = "crm.lead"

    _sql_constraints = [
        ('phone_uniq', 'unique (phone)', 'The Phone must be unique!')
    ]