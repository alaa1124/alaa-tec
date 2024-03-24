# -*- coding: utf-8 -*-
from odoo import exceptions
from odoo import api, fields, models 
from odoo import _
import time
import datetime
from datetime import datetime, date,timedelta
from dateutil import relativedelta
import sys

class account_voucher(models.Model):
    _inherit = "account.payment"

    real_estate_ref= fields.Char('Real Estate Ref.')
    ownership_line_id= fields.Many2one('loan.line.rs.own','Ownership Installment')
    rental_line_id= fields.Many2one('loan.line.rs.rent','Rental Contract Installment')

    # def post(self):
    #     res = super(account_voucher, self).post()
    #     for voucher in self:
    #         if (voucher.real_estate_ref) and (voucher.real_estate_ref)[:2]=='OC': #ownership contract
    #             installment_line_id = voucher.installment_line_id
    #             loan_line_rs_own_obj = self.env['loan.line.rs.own'].browse(installment_line_id)
    #             loan_line_rs_own_obj.write({'paid': True})
    #         if (voucher.real_estate_ref) and (voucher.real_estate_ref)[:2]=='RC': #rental contract 
    #             installment_line_id = voucher.installment_line_id
    #             loan_line_rs_rent_obj = self.env['loan.line.rs.rent'].browse(installment_line_id)
    #             loan_line_rs_rent_obj.write({'paid': True})
    #     return res
