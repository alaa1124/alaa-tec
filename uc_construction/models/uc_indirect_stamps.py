# -*- coding: utf-8 -*-

from odoo import models, fields,api


class IndirectStamps(models.Model):
    _name = "uc.indirect.stamps"
    _rec_name='stamp_id'
    company_currency = fields.Many2one("res.currency", string='Currency', default=lambda self:self.env.company.id)
    tender_id = fields.Many2one(
        string='Tender',
        comodel_name='uc.tender',
        ondelete='cascade',
        required=False,
    )

    stamp_id = fields.Many2one(
        string='stamp',
        comodel_name='uc.stamps',
        ondelete='cascade',
        required=True,
    )
    is_ordinary_stamps = fields.Boolean(string="Ordinary Stamps?",related='stamp_id.is_ordinary_stamps',store=True)
    is_additional_stamps = fields.Boolean(string="Additional Stamps?",related='stamp_id.is_additional_stamps',store=True)
    prectange = fields.Float(string="Prectange", required=False)

    value = fields.Monetary(string="Default Value",
                         required=False,
                         currency_field='company_currency',compute='_cal_value',store=True,readonly=False
                         )

    @api.depends('stamp_id.is_ordinary_stamps','stamp_id.is_additional_stamps','stamp_id','prectange')
    def _cal_value(self):
        for rec in self:
            if rec.stamp_id:
                if rec.stamp_id.is_ordinary_stamps:
                    rec.value = rec.tender_id.total_cost_all * (rec.prectange / 100)
                elif rec.stamp_id.is_additional_stamps:
                    ordinary_stamps =sum(self.env['uc.indirect.stamps'].search(
                        [('is_ordinary_stamps', '=', True)]).mapped('value'))
                    print("D>>>>>>>>>>>", ordinary_stamps)
                    rec.value = 3 * ordinary_stamps
                else:
                    rec.value = rec.stamp_id.value

