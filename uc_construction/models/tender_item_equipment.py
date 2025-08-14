from odoo import models, fields,api
from datetime import datetime



class TenderItemEquipment(models.Model):
    _name = 'tender.item.equipment'
    _description = 'all the equipments for each item'


    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self:self.env.user.company_id.currency_id.id)

    company_currency = fields.Many2one("res.currency", string='Currency', default=lambda self:self.env.company.id)

    tender_item_id = fields.Many2one(
        string='Item',
        comodel_name='uc.tender.item',
        ondelete='restrict',
    )
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        ondelete='restrict',
    )
    
    description = fields.Char(
        string='Description',
    )
    uom_id = fields.Many2one(
        string='Unit of measure',
        comodel_name='uom.uom',
        ondelete='restrict',related='product_id.uom_id',store=True
    )
    quantity = fields.Float(
        string='Quantity',
    )
    unitcost = fields.Monetary(
        string='Unit Cost',currency_field='currency_id',
    )
    
    subcost = fields.Monetary(
        string='sub Cost',currency_field='currency_id',compute="_calc_all",store=True,readonly=True
    )
    equipment_total_unit = fields.Float(
        string='Equipment total units',compute="_calc_all",store=True
    )
    equipment_total_cost = fields.Monetary(
        string='Equipment total cost',currency_field='currency_id',compute="_calc_all",store=True
    )
    equipment_total_cost_eg = fields.Monetary(
        string='Equipment total cost L.E',currency_field='company_currency',compute="_calc_all",store=True
    )
    total_cost_with_indirect_cost = fields.Monetary(
        string='Total_Cost_With_Indirect_Cost', currency_field='currency_id',
    )
    
    note = fields.Text(
        string='Note',
    )

    tag_ids = fields.Many2many('account.account.tag', 'itemequipment_account_account_tag', string='Tags', help="Optional tags you may want to assign for custom reporting")

    @api.depends( 'unitcost', 'currency_id', 'quantity')
    def _calc_all(self):
        for tec in self:
            tec.subcost = tec.unitcost * tec.quantity
            tec.equipment_total_unit = tec.tender_item_id.quantity * tec.quantity
            tec.equipment_total_cost = tec.subcost * tec.tender_item_id.quantity
            if tec.currency_id.id != self.env.company.currency_id.id:
                tec.equipment_total_cost_eg = tec.currency_id._convert(tec.equipment_total_cost, self.env.company.currency_id,
                                                              self.env.company, datetime.now().date())
            elif tec.currency_id.id == self.env.company.currency_id.id:
                tec.equipment_total_cost_eg = tec.equipment_total_cost
            else:
                tec.equipment_total_cost_eg = 0
    #currency
