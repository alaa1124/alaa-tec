
from odoo import models, fields,api
from datetime import datetime
class tenderIndirectOther(models.Model):
    _name = 'uc.indirect.other'
    _description = 'this model will contain all the other indirect costs'

    
    tender_id = fields.Many2one(
        string='Tender',
        comodel_name='uc.tender',
        ondelete='restrict',
    )
    name = fields.Char(
        string='Name',required='True',
    )
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self:self.env.user.company_id.currency_id.id)
    otherCost = fields.Monetary(
        string='Other Cost',currency_field='currency_id',
    )
    company_currency = fields.Many2one("res.currency", string='Currency', default=lambda self:self.env.company.id)

    otherCostEgy = fields.Monetary(
        string='Other Cost in L.E',currency_field="company_currency",
        compute='_clac_otherCostEgy',store=True
    )


    @api.depends('otherCost','currency_id')
    def _clac_otherCostEgy(self):
        for other in self:
            if other.currency_id.id!=self.env.company.currency_id.id:
                other.otherCostEgy = other.currency_id._convert(other.otherCost, self.env.company.currency_id, self.env.company,datetime.now().date())
            elif other.currency_id.id==self.env.company.currency_id.id:
                other.otherCostEgy=other.otherCost
            else:
                other.otherCostEgy = 0
