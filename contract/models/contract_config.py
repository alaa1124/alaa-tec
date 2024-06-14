from odoo import fields, models, api


class ContractConf(models.Model):
    _name = 'project.contract.conf'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Configuration accountin contract'
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)

    name = fields.Char(required=True)
    type = fields.Selection([('owner', 'Owner'), ('subconstructor', 'Subconstructor')], default='owner',
                            string="Type of Contract",required=True)
    parent_account_id = fields.Many2one("account.account",string="Partner account")
    revenue_account_id = fields.Many2one("account.account",string="Revenue Account")
