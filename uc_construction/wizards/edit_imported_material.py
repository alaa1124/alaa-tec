# -*- coding: utf-8 -*-

from odoo import fields, models, _,api
import xlsxwriter
import base64
import os


class ImportedMaterial(models.TransientModel):
    _name = 'imported.material.wiz'

    material_id= fields.Many2one(comodel_name="tender.item.material",readonly=True)
    isImported = fields.Boolean(
        string='is Imported'
    )

    custom_tax = fields.Selection(string="Custom  Tax",
                                  selection=[('percentage', 'Percentage'), ('amount', 'Amount'), ], required=False)
    custom_tax_value = fields.Float(
        string='custom_value',
    )
    vat_tax = fields.Selection(string="Vat  Tax", selection=[('percentage', 'Percentage'), ('amount', 'Amount'), ],
                               required=False)

    vat_tax_value = fields.Float(
        string='VAT Value',
    )
    comm_tax = fields.Selection(string="Comm  Tax", selection=[('percentage', 'Percentage'), ('amount', 'Amount'), ],
                                required=False)
    comm_tax_value = fields.Float(
        string='comm value',
    )

    administration_fees = fields.Float(
        string='administration_fees',
    )

    @api.model
    def default_get(self, fields):
        res=self.env['tender.item.material'].browse(self._context.get('active_ids'))
        result = super(ImportedMaterial, self).default_get(fields)
        result['isImported']=res.isImported
        result['custom_tax']=res.custom_tax
        result['custom_tax_value']=res.custom_tax_value
        result['vat_tax']=res.vat_tax
        result['vat_tax_value']=res.vat_tax_value
        result['comm_tax']=res.comm_tax
        result['comm_tax_value']=res.comm_tax_value
        result['administration_fees']=res.administration_fees
        return result

    def edit_item(self):
        self.material_id.write({
            'isImported':self.isImported,
            'custom_tax':self.custom_tax,
            'custom_tax_value':self.custom_tax_value,
            'vat_tax':self.vat_tax,
            'vat_tax_value':self.vat_tax_value,
            'comm_tax':self.comm_tax,
            'comm_tax_value':self.comm_tax_value,
            'administration_fees':self.administration_fees,
        })