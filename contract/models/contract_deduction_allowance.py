from odoo import fields, models, api


class DeductionAllowance(models.Model):
    _name = 'contract.deduction.allowance'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Deduction Allowance'

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)
    counterpart_account_id = fields.Many2one("account.account")
    type = fields.Selection([('owner', 'Owner'), ('subconstructor', 'Subconstructor')], default='owner',
                            string="Type of Contract", required=True)
    subtype = fields.Selection([('deduction', 'Deduction'), ('allowance', 'Allowance')],
                               string="main Type")
    calculation_type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')], default='percentage')
    amount = fields.Float("Amount")
    down_payment = fields.Boolean()




