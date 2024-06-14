from odoo import fields, models, api


class JobEstimat(models.Model):
    _inherit = "construction.job.cost"
    wbs_line_id = fields.Many2one("project.wbs.line")
    wbs_id = fields.Many2one(related='wbs_line_id.parent_id')
    previous_qty = fields.Float(compute='get_previous_qty')

    @api.depends('wbs_line_id','wbs_id')
    def get_previous_qty(self):
        for rec in self:
            rec.previous_qty = 0
            if rec.wbs_id and rec.id and rec.wbs_line_id:
                job_cost_id = self.env['construction.job.cost'].search(
                    [('techical_type', '=', True), ('wbs_line_id', '!=', rec.wbs_line_id.id),
                     ('wbs_id', '=',  rec.wbs_id.id),('state','!=','draft'),('item_id','=',rec.item_id.id)])
                if job_cost_id:
                     rec.previous_qty = sum(job_cost_id.mapped('qty'))


class Build(models.Model):
    _name = 'project.build'
    name = fields.Char(required=True)


class WBS(models.Model):
    _name = 'project.wbs'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'WBS'
    _rec_name = 'project_id'

    project_id = fields.Many2one("project.project", domain="[('state','=','confirm')]")
    partner_id = fields.Many2one("res.partner")
    state = fields.Selection([('draft', 'draft'), ('confirm', 'Confirm'), ('cancel', 'cancel')], default='draft')
    lines = fields.One2many("project.wbs.line", "parent_id")

    @api.onchange('project_id')
    def _onchange_project(self):
        if self.project_id:
            self.partner_id = self.project_id.partner_id.id if self.project_id.partner_id else ''

    def action_confirm(self):
        self.state = 'confirm'

    def action_cancel(self):
        self.state = 'cancel'


class WBSLines(models.Model):
    _name = 'project.wbs.line'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = "bulid_id"
    parent_id = fields.Many2one("project.wbs")
    bulid_id = fields.Many2one('project.build')
    project_id = fields.Many2one(related="parent_id.project_id", store=True)
    partner_id = fields.Many2one(related="parent_id.partner_id", store=True)
    state = fields.Selection(related="parent_id.state", store=True)
    is_techincal = fields.Boolean()

    def view_techincal(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Estimation',
            'view_mode': 'tree,form',
            'res_model': 'construction.job.cost',
            'target': 'current',
            'domain': [('active', 'in', (True, False)), ('wbs_line_id', '=', self.id)]

        }

    def action_create_techincal(self):
        job_cost_id = self.env['construction.job.cost'].search(
            [('techical_type', '=', False), ('project_id', '=', self.project_id.id), ('state', '=', 'quotation')])

        for rec in job_cost_id:
            new_job_id = rec.sudo().copy()

            new_job_id.state = 'draft'
            new_job_id.techical_type = True
            new_job_id.wbs_line_id = self.id
            new_job_id.actual_qty = new_job_id.tender_id.qty
            new_job_id.qty = 1
            new_job_id.currancy_id = new_job_id.currancy_id.id
            new_job_id.version_num = rec.version_num + 1
            version_num = rec.version_num + 1
            new_job_id.version = "V/" + str(rec.version_num + 1).zfill(5)



            self.duplicte_job_cost(new_job_id, rec)

        self.is_techincal = True

    def duplicte_job_cost(self, new_job_id, old_job_id):
        for rec in old_job_id.material_ids:
            new_line = rec.copy()
            new_line.job_id = new_job_id
            # new_line._compute_total_qty()
            # new_line._compute_total_value()

        for rec in old_job_id.labour_ids:
            new_line = rec.copy()
            new_line.job_id = new_job_id
            # new_line._compute_total_qty()
            # new_line._compute_total_value()

        for rec in old_job_id.expense_ids:
            new_line = rec.copy()
            new_line.job_id = new_job_id
            # new_line._compute_total_qty()
            # new_line._compute_total_value()

        for rec in old_job_id.subconstractor_ids:
            new_line = rec.copy()
            new_line.job_id = new_job_id
            # new_line._compute_cost_per_unit()
            # new_line._compute_total_value()

        for rec in old_job_id.equipment_ids:
            new_line = rec.copy()
            new_line.job_id = new_job_id
            # new_line._compute_cost_per_unit()
            # new_line._compute_cost_per_unit_with_qty()
