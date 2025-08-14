# -*- coding: utf-8 -*-

from odoo import models, fields,api


class IndirectTaxes(models.Model):
    _name = "uc.indirect.taxes"
    _rec_name='tax_id'


    tender_id = fields.Many2one(
        string='Tender',
        comodel_name='uc.tender',
        ondelete='cascade',
        required='True',
    )


    tax_id = fields.Many2one(
        string='Tax',
        comodel_name='account.tax',
        ondelete='cascade',
        required='True',
    )

    currency_id = fields.Many2one("res.currency", string='Currency', default=lambda self:self.env.company.id)

    value = fields.Monetary(string="Default Value",
                       compute="_calc_value",store=True,currency_field='currency_id'
                       )


    @api.depends('tax_id',)
    def _calc_value(self):
        for tax in self:
            tax.value=(tax.tax_id.amount/100)*tax.tender_id.total_cost