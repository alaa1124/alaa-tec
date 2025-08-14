from odoo import models, fields,api
from datetime import datetime



class TenderItemMaterial(models.Model):
    _name = 'tender.item.material'
    _description = 'all the materials needed for each item'
    _rec_name='product_id'


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
        ondelete='restrict',required=True
    )
    
    description = fields.Char(
        string='Description',
    )
    uom_id = fields.Many2one(
        string='Unit of measure',
        comodel_name='uom.uom',
        ondelete='restrict',related='product_id.uom_id',store=True
    )
    initial_quantity = fields.Float(
        string='Initial Quantity',
    )
    waste = fields.Float(
        string='Waste %',
    )
    final_quantity = fields.Float(
        string='Final Quantity',compute="_calc_all",store=True
    )

    
    isImported = fields.Boolean(
        string='is Imported',
    )

    custom_tax = fields.Selection(string="Custom  Tax", selection=[('percentage', 'Percentage'), ('amount', 'Amount'), ], required=False)
    custom_tax_value = fields.Float(
        string='custom_value',
    )
    vat_tax = fields.Selection(string="Vat  Tax", selection=[('percentage', 'Percentage'), ('amount', 'Amount'), ], required=False)


    vat_tax_value = fields.Float(
        string='VAT Value',
    )
    comm_tax = fields.Selection(string="Comm  Tax", selection=[('percentage', 'Percentage'), ('amount', 'Amount'), ], required=False)
    comm_tax_value = fields.Float(
        string='comm value',
    )
    
    administration_fees = fields.Float(
        string='administration_fees',
    )
    unitcost = fields.Monetary(
        string='Unit Cost',readonly=False,currency_field='currency_id'
    )
    
    subcost = fields.Monetary(
        string='sub Cost',compute="_calc_all",store=True,currency_field='currency_id'
    )
    material_total_unit = fields.Float(
        string='Material total units',compute="_calc_all",store=True,
    )
    material_total_cost = fields.Monetary(
        string='material total cost',currency_field='currency_id',compute="_calc_all",store=True
    )

    material_total_cost_egy = fields.Monetary(
        string='material total cost L.E',currency_field='company_currency',compute="_calc_all",store=True
    )
    note = fields.Text(
        string='Notes',
    )
    tax_ids = fields.Many2many('account.tax', 'item_material_tax',
        'item_material_id', 'tax_id', string='Default Taxes',
        )
    tag_ids = fields.Many2many('account.account.tag', 'itemmaterial_account_account_tag', string='Tags', help="Optional tags you may want to assign for custom reporting")



    @api.depends('initial_quantity','waste','currency_id','unitcost','custom_tax','custom_tax_value','vat_tax',
                 'vat_tax_value','comm_tax','comm_tax_value','administration_fees')
    def _calc_all(self):
        for mater in self:
            if mater.waste>0:
                mater.final_quantity=((mater.waste/100)*mater.initial_quantity)+mater.initial_quantity
            else:
                mater.final_quantity = mater.initial_quantity


            if mater.isImported:
                if mater.custom_tax_value == 'percentage':
                    mater.unitcost = (1+(mater.custom_tax_value / 100)) * mater.unitcost
                else:
                    mater.unitcost =mater.unitcost+ mater.custom_tax_value
                if mater.vat_tax == 'percentage':
                    mater.unitcost = (1+(mater.vat_tax_value / 100)) * mater.unitcost
                else:
                    mater.unitcost = mater.unitcost+mater.vat_tax_value
                if mater.comm_tax == 'percentage':
                    mater.unitcost = (1+(mater.comm_tax_value / 100)) * mater.unitcost
                else:
                    mater.unitcost =mater.unitcost+ mater.comm_tax_value
                mater.unitcost=mater.unitcost+mater.administration_fees
            mater.material_total_cost = (mater.subcost * mater.tender_item_id.quantity)
            mater.subcost = mater.unitcost * mater.final_quantity
            mater.material_total_unit = mater.tender_item_id.quantity * mater.final_quantity
            mater.material_total_cost = (mater.subcost * mater.tender_item_id.quantity)

            if mater.currency_id.id!=self.env.company.currency_id.id:
                mater.material_total_cost_egy = mater.currency_id._convert(mater.material_total_cost, self.env.company.currency_id, self.env.company,datetime.now().date())
            elif mater.currency_id.id==self.env.company.currency_id.id:
                mater.material_total_cost_egy=mater.material_total_cost
            else:
                mater.material_total_cost_egy = 0

    #currency
    #tax