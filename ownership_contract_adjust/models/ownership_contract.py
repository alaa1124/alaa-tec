from odoo import fields, models, api, _


class OwnerShip(models.Model):
    _inherit = 'ownership.contract'
    _description = 'maintenance deposit'

    handover_inst = fields.Float(string='Handover installment %', default=10, help="Handover installment amount in percent ex. 10")
    handover_inst_value = fields.Float("Handover installment Value")
    adv_pay = fields.Float(string='Adv. Payment %', default=25, help="Advance payment percent ex. 25")
    adv_pay_value = fields.Float("Adv. Payment Value")

    @api.onchange("adv_pay")
    def onchange_adv_Pay(self):
        self.adv_pay_value = (self.adv_pay / 100) * self.pricing

    @api.onchange("adv_pay_value")
    def calculate_adv_pay_value(self):
        self.adv_pay = (self.adv_pay_value / self.pricing) * 100

    @api.onchange("handover_inst")
    def onchange_handover_inst(self):
        self.handover_inst_value = (self.handover_inst / 100) * self.pricing

    @api.onchange("handover_inst_value")
    def calculate_handover_inst_value(self):
        self.handover_inst = (self.handover_inst_value / self.pricing) * 100
