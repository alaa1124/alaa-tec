# -*- coding: utf-8 -*-
from odoo import exceptions
from odoo import api, fields, models
from odoo import _
import time
import datetime
from datetime import datetime, date,timedelta
from dateutil import relativedelta
import sys


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    x_pan13_id = fields.Many2one(
        'account.analytic.account',
        string='كود الوحدة',

    )
    x_plan2_id = fields.Many2one(
        'account.analytic.account',
        string='جورنال بتاريخ',

    )
    x_plan3_id = fields.Many2one(
        'account.analytic.account',
        string='تويتر الفاتورة',

    )
    x_plan4_id = fields.Many2one(
        'account.analytic.account',
        string='جورنال ثابت',

    )
    x_plan5_id = fields.Many2one(
        'account.analytic.account',
        string='جورنال دائم',
    )
    x_plan6_id = fields.Many2one(
        'account.analytic.account',
        string='فواتير العملاء',
    )
    x_plan7_id = fields.Many2one(
        'account.analytic.account',
        string='ضريبة القيمة',
    )

    x_studio_main_plan_1 = fields.Char(related='x_plan7_id.plan_id.parent_id.name', store=True, string='Main Plan')
    x_studio_sub_plan_1 = fields.Char(related='x_plan7_id.plan_id.name', store=True, string='Sub-plan')
