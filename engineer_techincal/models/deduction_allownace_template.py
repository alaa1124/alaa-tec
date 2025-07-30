from odoo import fields, models, api


class Deduction(models.Model):
    _name = "engineer.deduction.lines"

    engineer_id = fields.Many2one("project.engineer.techincal")
    contract_type = fields.Selection([('owner', 'owner'), ('subconstructor', 'subconstructor')], default='owner',
                                     string="Type of Contract")
    name = fields.Many2one("contract.deduction.allowance",
                           domain="[('type','=',contract_type),('subtype','=','deduction')]")
    is_precentage = fields.Boolean(store=True)
    percentage = fields.Float(store=True)
    value = fields.Float(store=True, compute="onchange_is_precentage")
    counterpart_account_id = fields.Many2one("account.account", related='name.counterpart_account_id')
    amount_total_contract = fields.Float(related='engineer_id.amount_total_without_ded_allowance')

    # @api.depends('engineer_id', 'amount_total_contract', 'name', 'value')
    # def compute_percentage(rec):
    #     for self in rec:
    #         if self.name.calculation_type == 'percentage':
    #             self.percentage = self.name.amount
    #             self.is_precentage = True
    #         else:
    #             self.percentage = (self.amount_total_contract * 100) / self.value if self.value > 0 else 0

    @api.depends('engineer_id', 'amount_total_contract', 'percentage', 'is_precentage', 'name')
    def onchange_is_precentage(rec):
        for self in rec:
            if self.is_precentage and self.name.calculation_type == 'percentage':
                self.value = self.amount_total_contract * (self.percentage / 100)
            else:
                self.value = self.name.amount


class Allownace(models.Model):
    _name = "engineer.allowance.lines"

    engineer_id = fields.Many2one("project.engineer.techincal")
    contract_type = fields.Selection([('owner', 'owner'), ('subconstructor', 'subconstructor')], default='owner',
                                     string="Type of Contract")
    name = fields.Many2one("contract.deduction.allowance", domain="[('type','=',contract_type),\
    ('subtype','=','allowance')]")
    is_precentage = fields.Boolean()
    percentage = fields.Float()
    value = fields.Float(store=True, compute="onchange_is_precentage")
    counterpart_account_id = fields.Many2one("account.account", related='name.counterpart_account_id')

    amount_total_contract = fields.Float(related='engineer_id.amount_total_without_ded_allowance')


    @api.onchange('engineer_id', 'amount_total_contract', 'percentage', 'is_precentage', 'name')
    @api.depends('engineer_id', 'amount_total_contract', 'percentage', 'is_precentage', 'name')
    def onchange_is_precentage(rec):
        for self in rec:
            if self.name and self.percentage == 0:
                if self.name.calculation_type == 'percentage':
                    self.percentage = self.name.amount
                    self.is_precentage = True
                else:
                    self.value = self.name.amount

            if self.is_precentage == True:

                self.value = self.amount_total_contract * (self.percentage / 100)
            else:
                self.percentage = (self.amount_total_contract * 100) / self.value if self.value > 0 else 0


class Allownace(models.Model):
    _name = "engineer.allowance.lines"

    engineer_id = fields.Many2one("project.engineer.techincal")
    contract_type = fields.Selection([('owner', 'owner'), ('subconstructor', 'subconstructor')], default='owner',
                                     string="Type of Contract")
    name = fields.Many2one("contract.deduction.allowance", domain="[('type','=',contract_type),\
    ('subtype','=','allowance')]")
    is_precentage = fields.Boolean()
    percentage = fields.Float()
    value = fields.Float(store=True, compute="onchange_is_precentage")
    counterpart_account_id = fields.Many2one("account.account", related='name.counterpart_account_id')

    amount_total_contract = fields.Float(related='engineer_id.amount_total_without_ded_allowance')


    @api.onchange('engineer_id', 'amount_total_contract', 'percentage', 'is_precentage', 'name')
    @api.depends('engineer_id', 'amount_total_contract', 'percentage', 'is_precentage', 'name')
    def onchange_is_precentage(rec):
        for self in rec:
            if self.name and self.percentage == 0:
                if self.name.calculation_type == 'percentage':
                    self.percentage = self.name.amount
                    self.is_precentage = True
                else:
                    self.value = self.name.amount

            if self.is_precentage == True:

                self.value = self.amount_total_contract * (self.percentage / 100)
            else:
                self.percentage = (self.amount_total_contract * 100) / self.value if self.value > 0 else 0

