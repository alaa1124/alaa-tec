# -*- coding: utf-8 -*-

from odoo import models, fields, tools, api


class TenderItems(models.Model):
    _name = "uc.tender.item"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    header_id = fields.Many2one(comodel_name="uc.header", string="Header", required=False)

    name = fields.Char(
        string='Description'
    )

    sequence = fields.Integer(
        'Sequence', default=1, required=True,
        help="Gives the sequence order when displaying a list of work centers.")

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    tender_id = fields.Many2one(
        string='Tender',
        comodel_name='uc.tender',
        ondelete='cascade',
        required='True',
    )

    code = fields.Char(
        string='code', required='True',
    )
    root_id = fields.Many2one('item.root', compute='_compute_account_root', store=True)

    @api.depends('code')
    def _compute_account_root(self):
        for record in self:
            record.root_id = (ord(record.code[0]) * 1000 + ord(record.code[1:2] or '\x00')) if record.code else False

    quantity = fields.Float(
        string='Quantity',
    )
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        ondelete='restrict',
    )

    uom_id = fields.Many2one(
        string='Unit of measure',
        comodel_name='uom.uom',
        ondelete='restrict', related='product_id.uom_id', store=True
    )
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id)

    unit_cost = fields.Monetary(
        string='Unit Cost', currency_field='currency_id', compute="_calc_total_cost", store=True, readonly=False
    )

    total_cost_with_indirect_cost = fields.Monetary(
        string='Total Cost With Indirect Cost', currency_field='currency_id',ompute="_calc_total_cost",store=False
    )

    total_cost_before_overhead = fields.Monetary(
        string='Total Cost WithOut Overhead ', currency_field='currency_id', compute="_calc_total_cost", store=False
    )

    total_cost = fields.Monetary(
        string='Total Cost With Overhead', currency_field='currency_id', compute="_calc_total_cost", store=False
    )


    @api.depends('tender_item_materials', 'tender_item_equipments', 'tender_item_expenses', 'tender_item_labour',
                 'tender_item_overhead', 'tender_item_subcontractor','tender_item_lumps', 'quantity')
    def _calc_total_cost(self):
        for item in self:
            total = 0
            total += (sum(item.tender_item_materials.mapped('material_total_cost_egy')) + sum(
                item.tender_item_equipments.mapped('equipment_total_cost_eg')) + sum(
                item.tender_item_expenses.mapped('espense_total_cost_eg')) + sum(
                item.tender_item_labour.mapped('labour_total_cost_eg')) + sum(
                item.tender_item_subcontractor.mapped('subcontractor_total_cost_egy')))
            item.total_cost_before_overhead = total
            item.total_cost = total + sum(item.tender_item_overhead.mapped('overhead_total_cost_egy'))+sum(item.tender_item_lumps.mapped('value_egy'))
            try:
                item.total_cost_with_indirect_cost = (item.tender_id.total_cost_indirect * (item.total_cost / item.tender_id.total_cost_all))+item.total_cost
            except:
                item.total_cost_with_indirect_cost = 0
            try:
                item.unit_cost = item.total_cost / item.quantity
            except:
                item.unit_cost = 0

    note = fields.Text(
        string='Note',
    )

    infinancial = fields.Boolean(
        string='Add to financial Proposal',
        default=True
    )

    tag_ids = fields.Many2many('project.tags', 'tender_item_project_tag', string='Tags',
                               help="Optional tags you may want to assign for custom reporting")
    tender_item_materials = fields.One2many(comodel_name="tender.item.material", inverse_name="tender_item_id",
                                            string="Tender Products", required=False)
    tender_item_equipments = fields.One2many(comodel_name="tender.item.equipment", inverse_name="tender_item_id",
                                             string="Unit Equipment", required=False)
    tender_item_expenses = fields.One2many(comodel_name="tender.item.expense", inverse_name="tender_item_id",
                                           string="Unit Epenses", required=False)
    tender_item_labour = fields.One2many(comodel_name="tender.item.labour", inverse_name="tender_item_id",
                                         string="Unit Labours", required=False)
    tender_item_overhead = fields.One2many(comodel_name="tender.item.overhead", inverse_name="tender_item_id",string="Tender Overhead", required=False)
    tender_item_lumps = fields.One2many(comodel_name="tender.item.lumps", inverse_name="tender_item_id",string="Lump Sum Items", required=False)
    tender_item_subcontractor = fields.One2many(comodel_name="tender.item.subcontractor", inverse_name="tender_item_id",
                                                string="Tender Subcontractors", required=False)
    tender_item_materials_count = fields.Integer(compute='_compute_tender_item_materials_count',
                                                 string="Tender Item Materials Count")

    def _compute_tender_item_materials_count(self):
        items_data = self.env['tender.item.material'].read_group(
            [('tender_item_id', 'in', self.ids), ('isImported', '=', True)], ['tender_item_id'], ['tender_item_id'])
        result = dict((data['tender_item_id'][0], data['tender_item_id_count']) for data in items_data)
        for item in self:
            item.tender_item_materials_count = result.get(item.id, 0)

    def open_item_materials(self):
        action = self.env["ir.actions.actions"]._for_xml_id("uc_construction.tender_item_material_act_window")
        action['domain'] = [('tender_item_id', '=', self.id), ('isImported', '=', True)]
        return action


class AccountRoot(models.Model):
    _name = 'item.root'
    _description = 'item codes first 2 digits'
    _auto = False

    name = fields.Char()
    parent_id = fields.Many2one('item.root')

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
            CREATE OR REPLACE VIEW %s AS (
            SELECT DISTINCT ASCII(code) * 1000 + ASCII(SUBSTRING(code,2,1)) AS id,
                   LEFT(code,2) AS name,
                   ASCII(code) AS parent_id
            FROM uc_tender_item WHERE code IS NOT NULL
            UNION ALL
            SELECT DISTINCT ASCII(code) AS id,
                   LEFT(code,1) AS name,
                   NULL::int AS parent_id
                   
            FROM uc_tender_item WHERE code IS NOT NULL
            )''' % (self._table,)
                            )
