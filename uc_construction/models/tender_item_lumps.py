from odoo import models, fields,api
from datetime import datetime

class TenderItemLumps(models.Model):
    _name = 'tender.item.lumps'
    _description = 'all lumps for the item'



    tender_item_id = fields.Many2one(
        string='Item',
        comodel_name='uc.tender.item',
        ondelete='restrict',
    )
    name = fields.Char(
        string='Name', required='True',
    )
    value = fields.Float(string="Value", required=False)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id)
    company_currency = fields.Many2one("res.currency", string='Currency', default=lambda self: self.env.company.id)
    value_egy = fields.Monetary(
        string='Value L.E', currency_field='company_currency', compute="_calc_all", store=True,
        readonly=True
    )

    @api.depends('value','currency_id',)
    def _calc_all(self):
        for tec in self:
            if tec.currency_id.id != self.env.company.currency_id.id:
                tec.value_egy = tec.currency_id._convert(tec.value,
                                                                       self.env.company.currency_id,
                                                                       self.env.company, datetime.now().date())
            elif tec.currency_id.id == self.env.company.currency_id.id:
                tec.value_egy = tec.value
            else:
                tec.value_egy = 0

