from odoo import models, fields,api
from datetime import datetime

class TenderItemOverhead(models.Model):
    _name = 'tender.item.overhead'
    _description = 'all overheads for the item'



    tender_item_id = fields.Many2one(
        string='Item',
        comodel_name='uc.tender.item',
        ondelete='restrict',
    )
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self:self.env.user.company_id.currency_id.id)
    company_currency = fields.Many2one("res.currency", string='Currency', default=lambda self:self.env.company.id)

    overhead_type = fields.Selection(string="Overhead Type", selection=[('percentage', 'Percentage'), ('amount', 'Amount'), ], required=False)
    overhead_value = fields.Float(string="Overhead Value", required=False)
    profit_type = fields.Selection(string="Profit Type",
                                     selection=[('percentage', 'Percentage'), ('amount', 'Amount'), ], required=False)
    profit_value = fields.Float(string="Profit Value", required=False)

    tax_type = fields.Selection(string="Tax Type",
                                   selection=[('percentage', 'Percentage'), ('amount', 'Amount'), ], required=False)
    tax_value = fields.Float(string="Tax Value", required=False)

    
    overhead_total_cost = fields.Monetary(
        string='Overhead total cost',currency_field='currency_id',compute="_calc_all",store=True,readonly=True
    )

    overhead_total_cost_egy = fields.Monetary(
        string='overhead total cost L.E',currency_field='company_currency',compute="_calc_all",store=True,readonly=True
    )
    note = fields.Text(
        string='Notes',
    )
    
    tax_ids = fields.Many2many('account.tax', 'itemoverhead_account_tax_default_rel',
        'item_overhead_id', 'tax_id', string='Default Taxes')

    tag_ids = fields.Many2many('account.account.tag', 'teneroverhead_account_account_tag', string='Tags', help="Optional tags you may want to assign for custom reporting")

    @api.depends('overhead_type', 'overhead_value', 'profit_type','profit_value','tax_type','tax_value','currency_id','tender_item_id.total_cost_before_overhead')
    def _calc_all(self):
        for tec in self:
            overhead=profit=tax=sum=0
            if tec.overhead_type=='percentage':
                overhead=(tec.overhead_value/100)*tec.tender_item_id.total_cost_before_overhead
            else:
                overhead=tec.overhead_value
            if tec.profit_type=='percentage':
                profit=(tec.profit_value/100)*tec.tender_item_id.total_cost_before_overhead
            else:
                profit=tec.profit_value
            if tec.tax_type=='percentage':
                tax=(tec.tax_value/100)*tec.tender_item_id.total_cost_before_overhead
            else:
                tax=tec.tax_value
            sum=overhead+profit+tax
            tec.overhead_total_cost=sum
            if tec.currency_id.id != self.env.company.currency_id.id:
                tec.overhead_total_cost_egy = tec.currency_id._convert(tec.overhead_total_cost,
                                                                     self.env.company.currency_id,
                                                                     self.env.company, datetime.now().date())
            elif tec.currency_id.id == self.env.company.currency_id.id:
                tec.overhead_total_cost_egy = tec.overhead_total_cost
            else:
                tec.overhead_total_cost_egy = 0


    #currency
    #select percentage or value for overhead and profit
    #get the right tax place

    