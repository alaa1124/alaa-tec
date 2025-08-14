# -*- coding: utf-8 -*-

from odoo import models, fields,api


class Stamps(models.Model):
    _name = "uc.stamps"

    name = fields.Char(string="Stamp Name",
        required="True",
    )
    company_currency = fields.Many2one("res.currency", string='Currency', default=lambda self:self.env.company.id,currency_field='company_currency',)

    value = fields.Monetary(string="Default Value",
                       required=False,currency_field='company_currency'
                       )
    is_ordinary_stamps = fields.Boolean(string="Ordinary Stamps?")
    is_additional_stamps = fields.Boolean(string="Additional Stamps?")

