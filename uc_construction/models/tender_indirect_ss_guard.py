from odoo import models, fields,api
from datetime import datetime

class TenderIndirectSSGuard(models.Model):
    _name = 'uc.indirect.guard'
    _description = 'Cost of Guarding'
    _rec_name='gurad'
    

    
    tender_id = fields.Many2one(
        string='Tender',
        comodel_name='uc.tender',
        ondelete='restrict',
    )
    
    gurad = fields.Integer(
        string='Number of Guards',
    )
    duratation = fields.Integer(
        string='Duration in Months',
    )
    
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self:self.env.user.company_id.currency_id.id)
    company_currency = fields.Many2one("res.currency", string='Currency', default=lambda self:self.env.company.id)

    
    guard_salary = fields.Monetary(
        string='Monthly salary',currency_field='currency_id'
    )

    
    guarding_cost = fields.Monetary(
        string='Guarding Cost',currency_field='company_currency',compute="_calc_all",store=True
    )
    guarding_cost_egy = fields.Monetary(
        string='guarding Cost in L.E',currency_field='currency_id',compute="_calc_all",store=True
    )

    @api.depends('guard_salary', 'duratation', 'currency_id','gurad')
    def _calc_all(self):
        for grad in self:
            grad.guarding_cost = grad.guard_salary * grad.duratation*grad.gurad
            if grad.currency_id.id != self.env.company.currency_id.id:
                grad.guarding_cost_egy = grad.currency_id._convert(grad.guarding_cost, self.env.company.currency_id,
                                                            self.env.company, datetime.now().date())
            elif grad.currency_id.id == self.env.company.currency_id.id:
                grad.guarding_cost_egy = grad.guarding_cost
            else:
                grad.guarding_cost_egy = 0