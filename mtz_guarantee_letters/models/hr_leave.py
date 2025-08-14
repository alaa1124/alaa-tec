from odoo import models, fields, api
from datetime import timedelta

class HRLeave(models.Model):
    _inherit = 'hr.leave'

    @api.onchange('date_from', 'date_to')
    def _compute_leave_days(self):
        for leave in self:
            if leave.date_from and leave.date_to:
                if leave.date_from.date() == leave.date_to.date():
                    leave.number_of_days = 1
                else:
                    delta = leave.date_to - leave.date_from
                    leave.number_of_days = delta.days + 1 
