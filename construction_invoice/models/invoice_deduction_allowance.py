from odoo import fields, models, api


class Deduction(models.Model):
    _name = "invoice.deduction.lines"

    invoice_id = fields.Many2one("account.move", ondelete='cascade')
    contract_type = fields.Selection([('owner', 'owner'), ('subconstructor', 'subconstructor')], default='owner',
                                     string="Type of Contract")
    name = fields.Many2one("contract.deduction.allowance",
                           domain="[('type','=',contract_type),('subtype','=','deduction')]")
    is_precentage = fields.Boolean()
    percentage = fields.Float()
    value = fields.Float()
    counterpart_account_id = fields.Many2one("account.account", related='name.counterpart_account_id')
    amount_total_contract = fields.Float()
    invoice_line_id = fields.Many2one("account.move.line")

    @api.model
    def create(self, vals):
        res = super(Deduction, self).create(vals)
        if res.invoice_id:
            invoice_line_id = self.env['account.move.line'].sudo().create({
                'name': res.name.name,
                'account_id': res.counterpart_account_id.id if res.counterpart_account_id else '',
                'price_unit': -res.value,
                'display_type': 'product',
                'quantity': 1,
                'move_id': res.invoice_id.id,
                'tax_ids': [], 'is_ded_allow': True,
                'type_deduction_allownace': 'deduction'
            })
            res.invoice_line_id = invoice_line_id.id
        return res

    def write(self, vals):
        res = super(Deduction, self).write(vals)
        for rec in self:
            if rec.invoice_line_id:
                rec.invoice_line_id.name = rec.name.name
                rec.invoice_line_id.account_id = rec.counterpart_account_id.id if rec.counterpart_account_id else ''
                rec.invoice_line_id.price_unit = -rec.value
                rec.invoice_line_id.quantity = 1
                rec.invoice_line_id.is_ded_allow = True
                rec.invoice_line_id.type_deduction_allownace = 'deduction'

        return res

    @api.onchange('engineer_id', 'amount_total_contract', 'percentage', 'is_precentage', 'name')
    def onchange_is_precentage(self):
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
    _name = "invoice.allowance.lines"

    invoice_id = fields.Many2one("account.move", ondelete='cascade')
    contract_type = fields.Selection([('owner', 'owner'), ('subconstructor', 'subconstructor')], default='owner',
                                     string="Type of Contract")
    name = fields.Many2one("contract.deduction.allowance", domain="[('type','=',contract_type),\
    ('subtype','=','allowance')]")
    is_precentage = fields.Boolean()
    percentage = fields.Float()
    value = fields.Float()
    counterpart_account_id = fields.Many2one("account.account", related='name.counterpart_account_id')

    amount_total_contract = fields.Float()
    invoice_line_id = fields.Many2one("account.move.line")

    @api.model
    def create(self, vals):
        res = super(Allownace, self).create(vals)
        if res.invoice_id:
            invoice_line_id = self.env['account.move.line'].sudo().create({
                'name': res.name.name,
                'account_id': res.counterpart_account_id.id if res.counterpart_account_id else '',
                'price_unit': res.value,
                'display_type': 'product',
                'quantity': 1,
                'move_id': res.invoice_id.id,
                'tax_ids': [],
                'is_ded_allow': True,
                'type_deduction_allownace': 'allowance'
            })
            res.invoice_line_id = invoice_line_id.id
        return res

    def write(self, vals):
        res = super(Allownace, self).write(vals)
        for rec in self:
            if rec.invoice_line_id:
                rec.invoice_line_id.name = rec.name.name
                rec.invoice_line_id.account_id = rec.counterpart_account_id.id if rec.counterpart_account_id else ''
                rec.invoice_line_id.price_unit = rec.value
                rec.invoice_line_id.quantity = 1
                rec.invoice_line_id.is_ded_allow = True
                rec.invoice_line_id.type_deduction_allownace = 'allowance'
                # rec._onchange_is_precentage()
        return res

    @api.onchange('invoice_id.amount_total', 'amount_total_contract', 'percentage', 'is_precentage', 'name')
    def _onchange_is_precentage(self):
        if self.name and self.percentage == 0:
            if self.name.calculation_type == 'percentage':
                self.percentage = self.name.amount
                self.is_precentage = True
            else:
                self.value = self.name.amount

        if self.is_precentage == True:
            amount_total_contract = abs(sum(self.invoice_id.line_ids.mapped('debit')))

            self.value = amount_total_contract * (self.percentage / 100)
        else:
            self.percentage = (self.amount_total_contract * 100) / self.value if self.value > 0 else 0
