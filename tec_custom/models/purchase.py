from odoo import fields, models, api

import datetime
from dateutil.relativedelta import relativedelta
class PurchaseLine(models.Model):
    _inherit = 'purchase.order.line'
    order_date = fields.Datetime()
    delivery_period = fields.Float("Delivery Period")
    end_period = fields.Float("End Period")



class Purchase(models.Model):
    _inherit = 'purchase.order'
    order_date = fields.Datetime(copy=False)
    delivery_period = fields.Float("Delivery Period")
    end_period = fields.Float("End Period")
    start_date = fields.Date()
    delivery_date = fields.Date(compute='get_delivery_date')
    late_delivery = fields.Date()
    end_date = fields.Date(compute='get_delivery_date')

    @api.constrains('start_date','delivery_period')
    def get_late_delivery(self):
        if self.start_date:
             self.late_delivery = self.start_date + relativedelta(weeks=self.delivery_period)
    @api.depends('delivery_period','start_date','end_period','state')
    def get_delivery_date(self):
        for rec in self:
            rec.delivery_date=''
            rec.end_date=''
            if  rec.start_date:
                rec.delivery_date = rec.start_date+relativedelta(weeks=rec.delivery_period)


            if rec.start_date:
                rec.end_date = rec.start_date+relativedelta(weeks=rec.end_period)




    def button_confirm(self):
        res=super(Purchase, self).button_confirm()
        for rec in self:
            rec.order_date=datetime.datetime.today()
            if rec.delivery_date:
                for pick in rec.picking_ids:
                    if rec.delivery_date<pick.date_deadline:
                             pick.date_deadline = rec.delivery_date
                    pick.scheduled_date = rec.delivery_date


        return res
    def write(self,vals):

        res= super(Purchase, self).write(vals)
        if 'start_date' in vals:
            for rec in self.picking_ids:
                rec.scheduled_date=self.delivery_date
        return res


    # @api.model
    # def c


