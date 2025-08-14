from odoo import models, fields,api
from datetime import datetime

class TenderIndirectSSAccomodation(models.Model):
    _name = 'uc.indirect.accomodation'
    _description = 'Accomodations needs for the site'
    _rec_name='flat'
    

    
    tender_id = fields.Many2one(
        string='Tender',
        comodel_name='uc.tender',
        ondelete='restrict',
    )
    
    flat = fields.Integer(
        string='Number of Flats',
    )
    duratation = fields.Integer(
        string='Duration in Months',
    )
    
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self:self.env.user.company_id.currency_id.id)
    company_currency = fields.Many2one("res.currency", string='Currency', default=lambda self:self.env.company.id)

    flat_cost = fields.Monetary(
        string='Monthly Rent',currency_field='currency_id',
    )

    
    accomodation_cost = fields.Monetary(
        string='Accomodation Costs',currency_field='currency_id',compute="_calc_all",store=True
    )
    accomodation_cost_egy = fields.Monetary(
        string='Accomodation Costs in L.E',currency_field='company_currency',compute="_calc_all",store=True
    )

    @api.depends('flat_cost', 'duratation', 'currency_id','flat')
    def _calc_all(self):
        for acc in self:
            acc.accomodation_cost = acc.flat_cost * acc.duratation*acc.flat
            if acc.currency_id.id != self.env.company.currency_id.id:
                acc.accomodation_cost_egy = acc.currency_id._convert(acc.accomodation_cost, self.env.company.currency_id,
                                                            self.env.company, datetime.now().date())
            elif acc.currency_id.id == self.env.company.currency_id.id:
                acc.accomodation_cost_egy = acc.accomodation_cost
            else:
                acc.accomodation_cost_egy = 0