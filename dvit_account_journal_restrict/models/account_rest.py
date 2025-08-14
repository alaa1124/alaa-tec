from odoo import fields, models, api


class Journal(models.Model):
    _inherit = 'account.journal'
    is_show = fields.Boolean()

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        res = super().get_view(view_id, view_type, **options)
        if res['model']:

            journal_ids = self.env['account.journal'].sudo().search([])
            user = self.env['res.users'].search([('id', '=', self.env.uid)])

            for record in journal_ids:
                if self.env.user.journal_ids and self.env.user.has_group(
                        'dvit_account_journal_restrict.journal_restrict_group'):
                    if record.id in self.env.user.journal_ids.ids:
                        record.is_show = True
                    else:
                        record.is_show = False
                else:
                    record.is_show = True
        return res


class Move(models.Model):
    _inherit = 'account.move'

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if  self.env.user.journal_ids and self.env.user.journal_ids and self.env.user.has_group(
                        'dvit_account_journal_restrict.journal_restrict_group'):
            domain=[]
            domain.append(('id', '=', self.env.user.journal_ids.ids))
            if self.move_type in('out_invoice','out_refund'):
                domain.append(('type','=','sale'))
            if self.move_type in ('in_invoice', 'in_refund'):
                domain.append(('type', '=', 'purchase'))

            return {
                'domain': {'journal_id':domain}}
class Payment(models.Model):
    _inherit = 'account.payment'

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        if self.env.user.journal_ids and self.env.user.journal_ids and self.env.user.has_group(
                'dvit_account_journal_restrict.journal_restrict_group'):
            domain = []
            domain.append(('id', '=', self.env.user.journal_ids.ids))
            domain.append(('type', 'in',('bank','cash')))


            return {
                'domain': {'journal_id': domain}}
    @api.onchange('destination_journal_id')
    def _onchange_destination_journal_id(self):
        if self.env.user.journal_ids and self.env.user.journal_ids and self.env.user.has_group(
                'dvit_account_journal_restrict.journal_restrict_group'):
            domain = []
            domain.append(('id', '=', self.env.user.journal_ids.ids))
            domain.append(('type', 'in',('bank','cash')))


            return {
                'domain': {'destination_journal_id': domain}}

