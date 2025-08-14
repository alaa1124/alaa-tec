from odoo import models, fields,api
from datetime import datetime


class TenderIndirectSitesTechnician(models.Model):
    _name = 'tender.indirect.sites.technician'
    _description = 'this include all the costs of sites technician'

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
    technician_number = fields.Integer(
        string='Technician Number',
    )
    duration = fields.Integer(
        string='Duration in months',
    )
    month_cost = fields.Float(
        string='Month cost',
    )
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self:self.env.user.company_id.currency_id.id)
    company_currency = fields.Many2one("res.currency", string='Currency', default=lambda self:self.env.company.id)


    total_cost = fields.Monetary(
        string='Total Costs', currency_field='currency_id',compute="_calc_all",store=True
    )
    total_cost_egy = fields.Monetary(
        string='Total Costs in L.E', currency_field='company_currency',compute="_calc_all",store=True
    )


    @api.depends('month_cost', 'duration', 'currency_id','technician_number')
    def _calc_all(self):
        for tec in self:
            tec.total_cost = tec.month_cost * tec.duration*tec.technician_number
            if tec.currency_id.id != self.env.company.currency_id.id:
                tec.total_cost_egy = tec.currency_id._convert(tec.total_cost, self.env.company.currency_id,
                                                            self.env.company, datetime.now().date())
            elif tec.currency_id.id == self.env.company.currency_id.id:
                tec.total_cost_egy = tec.total_cost
            else:
                tec.total_cost_egy = 0

