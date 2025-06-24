from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'analytic.mixin']

    @api.onchange('analytic_distribution')
    def onchange_analytic_distribution(self):
        for line in self.order_line:
            line.analytic_distribution = self.analytic_distribution


class StockMove(models.Model):
    _name = 'stock.move'
    _inherit = ['stock.move', 'analytic.mixin']

    def _action_confirm(self, merge=False, merge_into=False):
        return super()._action_confirm(merge=merge, merge_into=merge_into)

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res.analytic_distribution = res.purchase_line_id.order_id.analytic_distribution
        return res


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'analytic.mixin']

    @api.model
    def create(self, vals):
        res = super().create(vals)
        analytic_distribution = res.analytic_distribution

        if not self.env.context.get('analytic_distribution'):
            stock_analytic = res.stock_move_id.analytic_distribution
            purchase_analytic = res.line_ids.purchase_line_id.order_id.analytic_distribution
            res.analytic_distribution = stock_analytic or purchase_analytic
        if not res.analytic_distribution:
            res.analytic_distribution = analytic_distribution

        # res.line_ids.write({'analytic_distribution': res.analytic_distribution})

        return res








