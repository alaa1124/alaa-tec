from odoo import models, fields,api
from datetime import datetime
class TenderIndirectPSTravel(models.Model):
    _name = 'tender.indirect.travel'
    _description = 'this include all the costs of Travel'
    _rec_name='trip'


    
    tender_id = fields.Many2one(
        string='Tender',
        comodel_name='uc.tender',
        ondelete='restrict',
    )
    
    trip = fields.Integer(
        string='Number of Trips',
    )
    engineer = fields.Integer(
        string='Number of Engineers',
    )
    no_of_days= fields.Integer(string="Number of Days", required=False)
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self:self.env.user.company_id.currency_id.id)
    
    air_ticket_cost = fields.Monetary(
        string='Air tickets Costs',currency_field='currency_id',
    )

    accomodation_cost = fields.Monetary(
        string='Accomodation Costs',currency_field='currency_id',
    )
    pirdeem_cost = fields.Monetary(
        string='Pocket Money',currency_field='currency_id',
    )
    company_currency = fields.Many2one("res.currency", string='Currency', default=lambda self:self.env.company.id)
    travel_cost = fields.Monetary(
        string='Travel Costs',currency_field='currency_id',compute='_calc_all',store=True
    )
    travel_cost_egy = fields.Monetary(
        string='Travel Costs in L.E',currency_field='company_currency',compute='_calc_all',store=True
    )

    @api.depends('accomodation_cost', 'air_ticket_cost','engineer', 'currency_id','trip','no_of_days','accomodation_cost','pirdeem_cost')
    def _calc_all(self):
        print("F:::::::::::::::::::::::")
        for trav in self:
            trav.travel_cost =(trav.air_ticket_cost*trav.engineer)+(trav.trip*trav.engineer*trav.no_of_days*(trav.accomodation_cost+trav.pirdeem_cost))
            print(">D>>D",trav.travel_cost)
            if trav.currency_id.id != self.env.company.currency_id.id:
                trav.travel_cost_egy = trav.currency_id._convert(trav.travel_cost, self.env.company.currency_id,
                                                            self.env.company, datetime.now().date())
            elif trav.currency_id.id == self.env.company.currency_id.id:
                trav.travel_cost_egy = trav.travel_cost
            else:
                trav.travel_cost_egy = 0


