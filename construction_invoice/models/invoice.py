from odoo import fields, models, api, _

from datetime import datetime

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class Account_move(models.Model):
    _inherit = "account.move"

    show_commercial_partner_warning = fields.Boolean()
    show_update_fpos = fields.Boolean()

    def action_update_fpos_values(self):
        pass

    project_id = fields.Many2one("project.project", domain=[('state', '=', 'confirm')])
    contract_id = fields.Many2one("project.contract",
                                  domain="[('is_subcontract','=',False),('project_id','=',project_id)]")
    type = fields.Selection([('owner', 'Owner'), ('subconstructor', 'Subcontractor')],
                            string="Type of Contract")
    sub_type = fields.Selection([('process', 'Process'), ('final', 'Final')],default='process', string="Type", required=True)
    deduction_ids = fields.One2many("invoice.deduction.lines","invoice_id")
    allowance_ids = fields.One2many("invoice.allowance.lines","invoice_id")
    amount_deduction = fields.Monetary(compute='_compute_deduction_allowane')
    amount_allowance = fields.Monetary(compute='_compute_deduction_allowane')
    amount_due_value = fields.Monetary(compute='_compute_amount_due_value')
    account_id = fields.Many2one('account.account')

    @api.depends('amount_deduction','amount_allowance','amount_total')
    def _compute_amount_due_value(self):
        for rec in self:
            rec.amount_due_value=rec.amount_total_signed

    @api.depends('deduction_ids','allowance_ids')
    def _compute_deduction_allowane(self):
        for rec in self:
            rec.amount_deduction=0
            rec.amount_allowance=0
            for line in rec.deduction_ids:
                rec.amount_deduction+=line.value
            for line in rec.allowance_ids:
                rec.amount_allowance+=line.value


    eng_id = fields.Many2one("project.engineer.techincal")

    invoice_line_ids = fields.One2many(  # /!\ invoice_line_ids is just a subset of line_ids.
        'account.move.line',
        'move_id',
        string='Invoice lines',
        copy=False,
        readonly=True,
        domain=[('is_ded_allow','=',False),('display_type', 'in', ('product', 'line_section', 'line_note'))],
        states={'draft': [('readonly', False)]},
    )

    @api.depends(
        'line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual',
        'line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency',
        'line_ids.balance',
        'line_ids.currency_id',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state',
        'line_ids.full_reconcile_id','deduction_ids','allowance_ids')
    def _compute_amount(self):
        res = super(Account_move,self)._compute_amount()
        for rec in self:
            if rec.deduction_ids:
                rec.amount_total=rec.amount_total-sum(rec.deduction_ids.mapped('value'))
            if rec.allowance_ids:
                rec.amount_total = rec.amount_total + sum(rec.allowance_ids.mapped('value'))
        return res

    # def action_register_payment(self):
    #     res = super().action_register_payment()
    #     res['context']={
    #         'active_model': 'account.move',
    #         'active_ids': self.ids,


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    has_abnormal_deferred_dates = fields.Boolean()


    is_ded_allow = fields.Boolean()
    type_deduction_allownace = fields.Selection([('deduction','Deduction'),('allowance','Allowance')])
    project_id = fields.Many2one("project.project", related='move_id.project_id', store=True, index=True)
    contract_id = fields.Many2one("project.contract", related='move_id.contract_id', store=True, index=True)
    contract_type = fields.Selection([('owner', 'owner'), ('subconstructor', 'subconstructor')], default='owner',
                                     string="Type of Contract")

    detailed_line = fields.Many2one('project.contract.stage.line',
                                    store=True, readonly=False)
    item = fields.Many2one("project.item", store=True, readonly=False)
    item_line = fields.Many2one("project.tender", store=True, readonly=False)
    stage_id = fields.Many2one("project.stage", related='detailed_line.stage_id.stage_id', store=True, readonly=False)

    @api.onchange('detailed_line')
    def onchange_detailed_line(self):
        if self.detailed_line:
            self.name = self.detailed_line.name

    @api.constrains('account_id', 'display_type')
    def _check_payable_receivable(self):
        for line in self:
            account_type = line.account_id.account_type
            # if line.move_id.is_sale_document(include_receipts=True):
                # if (line.display_type == 'payment_term') ^ (account_type == 'asset_receivable'):
                #     raise UserError(_("Any journal item on a receivable account must have a due date and vice versa."))
            if line.move_id.is_purchase_document(include_receipts=True):
                if (line.display_type == 'payment_term') ^ (account_type == 'liability_payable'):
                    raise UserError(_("Any journal item on a payable account must have a due date and vice versa."))