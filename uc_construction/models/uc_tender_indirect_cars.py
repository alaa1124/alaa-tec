# -*- coding: utf-8 -*-

from odoo import models, fields,api
from datetime import datetime




class TenderIndirectCars(models.Model):
    _name = 'uc.indirect.cars'
    _description = 'The Details of Cars for the tender'
    _rec_name='car'


    tender_id = fields.Many2one(
        string='Tender',
        comodel_name='uc.tender',
        ondelete='restrict',
    )
    
    car = fields.Integer(
        string='Number of Cars',
    )
    duration = fields.Integer(
        string='Duration in months',
    )
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self:self.env.user.company_id.currency_id.id)
    company_currency = fields.Many2one("res.currency", string='Currency', default=lambda self:self.env.company.id)
    cost= fields.Float(string="Cost / Month", required=False)
    car_cost = fields.Monetary(
        string='Total Car Costs',currency_field='currency_id',compute="_calc_all",store=True
    )
    car_cost_egy = fields.Monetary(
        string='Total Car Costs L.E',currency_field='currency_id',compute="_calc_all",store=True
    )



    @api.depends('cost','car','currency_id')
    def _calc_all(self):
        for car in self:
            car.car_cost=car.car*car.cost
            if car.currency_id.id!=self.env.company.currency_id.id:
                car.car_cost_egy = car.currency_id._convert(car.car_cost, self.env.company.currency_id, self.env.company,datetime.now().date())
            elif car.currency_id.id==self.env.company.currency_id.id:
                car.car_cost_egy=car.car_cost
            else:
                car.car_cost_egy = 0