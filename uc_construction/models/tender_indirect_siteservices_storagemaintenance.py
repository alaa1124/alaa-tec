
from odoo import models, fields,api
from datetime import datetime

class TenderIndirectSites(models.Model):
    _name = 'uc.indirect.sites'
    _description = 'Cost of Sites'

    tender_id = fields.Many2one(
        string='Tender',
        comodel_name='uc.tender',
        ondelete='restrict',
    )
    # site_service_type_id = fields.Many2one(
    #     string='SiteService Type',
    #     comodel_name='uc.site.service.type',
    #     ondelete='restrict',
    # )
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self:self.env.user.company_id.currency_id.id)
    company_currency = fields.Many2one("res.currency", string='Currency', default=lambda self:self.env.company.id)

    storage_cost = fields.Monetary(
        string='Storage Cost', currency_field='currency_id'
    )
    maintenanceCost = fields.Monetary(
        string='Maintenance Cost', currency_field='currency_id'
    )

    total_cost = fields.Monetary(
        string='Total Costs', currency_field='currency_id',compute="_calc_all",store=True
    )
    total_cost_egy = fields.Monetary(
        string='Total Costs in L.E', currency_field='company_currency',compute="_calc_all",store=True
    )

    @api.depends('storage_cost', 'maintenanceCost', 'currency_id')
    def _calc_all(self):
        for tec in self:
            tec.total_cost = tec.storage_cost * tec.maintenanceCost
            if tec.currency_id.id != self.env.company.currency_id.id:
                tec.total_cost_egy = tec.currency_id._convert(tec.total_cost, self.env.company.currency_id,
                                                              self.env.company, datetime.now().date())
            elif tec.currency_id.id == self.env.company.currency_id.id:
                tec.total_cost_egy = tec.total_cost
            else:
                tec.total_cost_egy = 0

