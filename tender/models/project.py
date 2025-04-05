from odoo import models, fields, api, _

from datetime import datetime
from odoo.exceptions import ValidationError
import json
import io
import base64
from odoo.tools import date_utils

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class Projects(models.Model):
    _inherit = "project.project"

    open_task_count = fields.Integer()

    def _default_currency_id(self):
        return self.env.user.company_id.currency_id

    state = fields.Selection([('draft', 'draft'), ('confirm', 'confirm')], default='draft')
    is_tender = fields.Boolean()
    project_number = fields.Char()
    project_refernce = fields.Char()
    tender_ids = fields.One2many("project.tender", "project_id")
    currency_ids = fields.One2many("project.currency", "project_id")
    created_date = fields.Date("Created Date", default=datetime.today(), tracking=True)
    consultant = fields.Many2one("res.partner", string="Consultant", tracking=True)

    manager_id = fields.Many2one("res.partner", string="Manager", tracking=True)
    is_quotation = fields.Boolean(tracking=True)
    date_from = fields.Date("Project Begining", tracking=True)
    date_to = fields.Date("Project End Date", tracking=True)
    dif = fields.Char("Differance", compute='get_differance')
    date_contract = fields.Date("Contract Date", tracking=True)
    tender_submission_date = fields.Date(tracking=True)
    location_acquisition_date = fields.Date(tracking=True)
    currancy_id = fields.Many2one("res.currency", default=lambda self: self._default_currency_id())
    # working_prec = fields.Float("نسبه الانجاز")
    job_cost_count = fields.Integer(compute='get_job_cost_count')
    total_direct_cost = fields.Float(compute='compute_total_direct_cost')
    indirect_id = fields.Many2one("indirect.cost")
    profit_id = fields.Many2one("top.sheet")
    total_direct_indirect = fields.Float(compute='get_total_direct_indirect')
    quotation_count = fields.Integer(copy=False, compute='get_quotation_count')
    is_quotation = fields.Boolean()
    def get_quotation_count(self):
        for rec in self:
            rec.quotation_count = 0
            if rec.id:
                quotation_count_ids = self.env['construction.sale.order'].sudo().search(
                    [('active', 'in', (False, True)), ('project_id', '=', rec.id)])
                rec.quotation_count = len(quotation_count_ids)

    @api.depends('tender_ids')
    def get_total_direct_indirect(self):
        for rec in self:
            rec.total_direct_indirect = sum(rec.tender_ids.mapped('total_direct')) + sum(
                rec.tender_ids.mapped('total_indirect'))

    def view_quotation(self):
        view = self.env.ref('tender.construction_sale_order_tree')
        view_form = self.env.ref('tender.construction_sale_order_form')

        return {
            'type': 'ir.actions.act_window',
            'name': 'Financial Offer',
            'view_mode': 'tree,form',
            'res_model': 'construction.sale.order',
            'domain': [('active', 'in', (False, True)), ('project_id', '=', self.id)],
            'views': [(view.id, 'tree'), (view_form.id, 'form')],
            # 'context': {"search_default_version": 1},
            'target': 'current',

        }

    @api.constrains('tender_ids', 'indirect_id','profit_id')
    def _check_tender_ids(self):
        if self.indirect_id:
            total_indirect = sum(self.tender_ids.mapped('total_indirect'))
            if int(self.indirect_id.total) < int(total_indirect):
                raise ValidationError("Total Indirect cost must equal %s" % (round(self.indirect_id.total, 2)))
        if self.profit_id:
            total_profit = sum(self.tender_ids.mapped('total_profit'))
            if int(self.profit_id.total) < int(total_profit):
                raise ValidationError("Total Profit cost must equal %s" % (round(self.profit_id.total, 2)))

    @api.depends('tender_ids')
    def compute_total_direct_cost(self):
        for rec in self:
            rec.total_direct_cost = sum(rec.tender_ids.mapped('total_direct'))

    def update_currency(self):
        job_ids = self.env['construction.job.cost'].search([('project_id', '=', self.id), ('state', '=', 'draft')])
        for rec in job_ids:
            for mat in rec.material_ids:
                mat.onchange_currancy_id()

    @api.depends('name')
    def get_job_cost_count(self):
        for rec in self:
            rec.job_cost_count = 0
            if rec.id:
                job_ids = self.env['construction.job.cost'].search([('project_id', '=', rec.id)],
                                                                   order='version_num desc', limit=1)
                rec.job_cost_count = (job_ids.version_num)

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

    def upload_tender(self):
        view = self.env.ref('comman_module.mutli_edit_tender_view_tree')

        return {
            'type': 'ir.actions.act_window',
            'name': 'Upload Tender ',
            'view_mode': 'tree',
            'view_id': view.id,
            'res_model': 'project.tender',
            'domain': [('state', '=', 'main'), ('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
            'target': 'current',

        }

    def view_estimation(self):

        return {
            'type': 'ir.actions.act_window',
            'name': 'Estimation',
            'view_mode': 'tree,form',
            'res_model': 'construction.job.cost',
            'context': {'default_project_id': self.id, "search_default_version": 1},
            'target': 'current',
            'domain': [('techical_type','=',False),('active', 'in', (True, False)), ('project_id', '=', self.id)]

        }

    def create_job_ct(self):

        job_cost_count = 0
        self.clear_caches()
        job_cost_ids = self.env['construction.job.cost'].sudo().search(
            [('techical_type', '=', False), ('project_id', '=', self.id)])
        job_cost_ids_2 = self.env['construction.job.cost'].sudo().search(
            [('techical_type', '=', False), ('active', '=', False), ('project_id', '=', self.id)])

        version_num = 1
        if job_cost_ids:
            for rec in job_cost_ids:
                new_job_id = rec.sudo().copy()

                new_job_id.state = 'draft'
                new_job_id.qty = new_job_id.tender_id.qty
                new_job_id.currancy_id = self.currancy_id.id
                new_job_id.version_num = rec.version_num + 1
                version_num = rec.version_num + 1
                new_job_id.version = "V/" + str(rec.version_num + 1).zfill(5)

                rec.active = False

                self.duplicte_job_cost(new_job_id, rec)
                # new_job_id._compute_all_values()

            # self.job_cost_count = len(job_cost_ids)+len(job_cost_ids_2)
            if len(job_cost_ids) != len(self.tender_ids):
                for tend in self.tender_ids:
                    job_cost_id = self.env['construction.job.cost'].sudo().search(
                        [('techical_type', '=', False), ('tender_id', '=', tend.id), ('project_id', '=', self.id)])

                    if not job_cost_id and not tend.display_type:
                        # self.job_cost_count+=1
                        tend.state = 'job_cost'
                        self.env['construction.job.cost'].sudo().create({
                            # 'name': 'Job Cost/' + rec.code,
                            'project_id': tend.project_id.id,
                            'partner_id': self.partner_id.id if self.partner_id else '',
                            'code': tend.code,
                            'item_id': tend.item.id,
                            'description': tend.name,
                            'uom_id': tend.uom_id.id,
                            'qty': tend.qty,

                            'note': tend.note,
                            'tender_id': tend.id,
                            'related_job_id': tend.related_job_id.id,
                            'currancy_id': self.currancy_id.id,
                            'version_num': version_num,
                            'version': "V/" + str(version_num).zfill(5),
                        }
                        )


        else:
            for rec in self.tender_ids:

                job_id = self.env['construction.job.cost'].sudo().search(
                    [('techical_type', '=', False), ('tender_id', '=', rec.id)])

                if rec.display_type == False:
                    job_cost_count += 1
                    rec.state = 'job_cost'
                    self.env['construction.job.cost'].sudo().create({
                        # 'name': 'Job Cost/' + rec.code,
                        'project_id': rec.project_id.id,
                        'partner_id': self.partner_id.id if self.partner_id else '',
                        'code': rec.code,
                        'item_id': rec.item.id,
                        'description': rec.name,
                        'uom_id': rec.uom_id.id,
                        'qty': rec.qty,

                        'note': rec.note,
                        'tender_id': rec.id,
                        'related_job_id': rec.related_job_id.id,
                        'version_num': 1,
                        'version': "V/" + str(1).zfill(5),
                    }
                    )

            # self.job_cost_count = job_cost_count

    @api.depends('date_to', 'date_from')
    def get_differance(self):
        for rec in self:
            rec.dif = ''
            if rec.date_from and rec.date_to:
                rec.dif = rec.date_to - rec.date_from

    @api.model
    def create(self, vals):
        res = super(Projects, self).create(vals)
        res.project_number = self.env["ir.sequence"].next_by_code("project.code")
        return res

    def action_confirm_project(self):
        self.state = 'confirm'
    def create_quotation(self):
        sales_order = self.env['construction.sale.order'].sudo().search([('project_id', '=', self.id)], order='id asc')
        sales_order_all_ids = self.env['construction.sale.order'].sudo().search(
            [('active', 'in', (False, True)), ('project_id', '=', self.id)], order='id asc')
        self.is_quotation = True
        job_cost_ids = self.env['construction.job.cost'].sudo().search(
            [('techical_type', '=', False), ('project_id', '=', self.id), ('state', '=', 'quotation')])

        lines = []
        version_num = estimation_version = 1

        for rec in self.tender_ids:
            job_cost_ids = self.env['construction.job.cost'].sudo().search(
                [('techical_type', '=', False), ('project_id', '=', self.id), ('tender_id', '=', rec.id),
                 ('state', '=', 'quotation')])
            if job_cost_ids:
                estimation_version = job_cost_ids.version_num
                if rec.display_type == False:
                    lines.append((0, 0, {
                        'name': rec.code,
                        'description': rec.name,
                        'item': rec.item.id,
                        'qty': rec.qty,
                        'uom_id': rec.uom_id.id,
                        'price_unit': rec.sale_price,
                        'price': rec.sale_price/rec.qty,
                        'total_value': rec.sale_price,

                        'tender_id': rec.id,
                        'display_type': rec.display_type

                    }))
            if rec.display_type != False:
                lines.append((0, 0, {
                    'name': rec.name,
                    'display_type': rec.display_type

                }))

        name_so = ''
        if sales_order:
            version_num = len(sales_order_all_ids) + 1

            for rec in sales_order:
                name_so = rec.name

                rec.active = False

            # sales_order.write({
            #     'partner_id': self.partner_id.id,
            #     'project_id': self.id,
            #     'order_lines': lines, 'created_date': self.created_date,
            # })

        if lines:
            sales = self.env['construction.sale.order'].sudo().create({
                'partner_id': self.partner_id.id,
                'project_id': self.id,
                'order_lines': lines, 'created_date': self.created_date,
                'version_num': version_num,
                'version': "V/" + str(version_num).zfill(5),
                'estimation_version': "V/" + str(estimation_version).zfill(5),
            })
            if name_so:
                sales.name = name_so
            else:

                sales.name = "QUT/" + str(sales.id).zfill(6)

            self.is_quotation=True


