from odoo import fields, models, api


class Payment(models.Model):
    _inherit = "account.payment"
    project_id = fields.Many2one("project.project", domain=[('state', '=', 'confirm')])
    contract_id = fields.Many2one("project.contract",
                                  domain="[('is_subcontract','=',False),('project_id','=',project_id)]")
    type = fields.Selection([('owner', 'owner'), ('subconstructor', 'subconstructor')], default='owner',
                            string="Type of Contract")

    @api.depends('move_id.line_ids.matched_debit_ids', 'move_id.line_ids.matched_credit_ids')
    def _compute_stat_buttons_from_reconciliation(self):
        res = super(Payment,self)._compute_stat_buttons_from_reconciliation()
        for rec in self:
            if len(rec.reconciled_invoice_ids)==1:
                for inv in rec.reconciled_invoice_ids:
                    rec.project_id=inv.project_id.id if inv.project_id else ''
                    rec.contract_id=inv.contract_id.id if inv.contract_id else ''
                    rec.type=inv.type
        return res


    # def action_post(self):
    #     res = super(Payment,self).action_post()
    #     for rec in self:
    #
    #         if len(rec.reconciled_invoice_ids)==1:
    #             for inv in rec.reconciled_invoice_ids:
    #                 rec.project_id=inv.project_id.id if inv.project_id else ''
    #                 rec.contract_id=inv.contract_id.id if inv.contract_id else ''
    #                 rec.type=inv.type
    #     return res
    # def write(self,vals):
    #     res = super(Payment,self).write(vals)
    #     if 'reconciled_invoice_ids' in vals:
    #         for rec in self:
    #             if len(rec.reconciled_invoice_ids)==1:
    #                 for inv in rec.reconciled_invoice_ids:
    #                     rec.project_id=inv.project_id.id if inv.project_id else ''
    #                     rec.contract_id=inv.contract_id.id if inv.contract_id else ''
    #                     rec.type=inv.type
    #     return res

class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'
    project_id = fields.Many2one("project.project", domain=[('state', '=', 'confirm')])
    contract_id = fields.Many2one("project.contract",
                                  domain="[('is_subcontract','=',False),('project_id','=',project_id)]")
    type = fields.Selection([('owner', 'owner'), ('subconstructor', 'subconstructor')], default='owner',
                            string="Type of Contract")


    # def  _create_payments(self):
    #     red = super(AccountPaymentRegister,self)._create_payments()
    #     for rec in res:


