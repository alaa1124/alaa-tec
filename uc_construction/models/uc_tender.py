# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Tender(models.Model):
    _name = "uc.tender"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    name = fields.Char(string="Name",
                       required="True",
                       )

    description = fields.Char(
        string="Description",
        required="True",
    )

    customer_id = fields.Many2one(
        string="Customer",
        comodel_name="res.partner",
        ondelete="restrict",
    )

    consultant_id = fields.Many2one(
        string="Consultant",
        comodel_name="res.partner",
        ondelete="restrict",
    )

    projectmanager_id = fields.Many2one(
        string="Project Manager",
        comodel_name="res.partner",
        ondelete="restrict",
    )

    start_date = fields.Date(
        string="Starting Date",
    )
    end_date = fields.Date(
        string="End Date",
    )

    note = fields.Text(
        string="Note",
    )
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self:self.env.user.company_id.currency_id.id)


    consultancy_fees = fields.Monetary(
        string="Consultancy fees", compute="_calc_all", store=True
    )
    stamp_fees = fields.Monetary(
        string="Stamps fees", compute="_calc_all", store=False
    )
    taxes_fees = fields.Monetary(
        string="Taxes fees", compute="_calc_all", store=False
    )
    bank_fees = fields.Monetary(
        string="Bank fees", compute="_calc_all", store=True
    )
    clearing_fees = fields.Monetary(
        string="Clearing fees", compute="_calc_all", store=True
    )
    site_fees = fields.Monetary(
        string="Site Services fees", compute="_calc_all", store=True
    )
    Project_fees = fields.Monetary(
        string="Project Services fees", compute="_calc_all", store=True
    )
    other_fees = fields.Monetary(
        string="Others fees", compute="_calc_all", store=True
    )
    total_cost = fields.Monetary(
        string="Total Cost", compute="_calc_all", store=True
    )

    tag_ids = fields.Many2many(
        "project.tags",
        "tender_project_tag",
        string="Tags",
        help="Optional tags you may want to assign for custom reporting",
    )
    total_cost_indirect = fields.Monetary(
        string='Indirect Cost', compute="_calc_all"
    )
    total_cost_direct = fields.Monetary(
        string='All Direct Cost', compute="_calc_all"
    )
    total_cost_all = fields.Monetary(
        string='Total Cost', compute="_calc_all"
    )
    total_cars = fields.Monetary(
        compute="_calc_all"
    )
    total_travels = fields.Monetary(
        compute="_calc_all"
    )
    total_technician = fields.Monetary(
        compute="_calc_all"
    )

    total_guard = fields.Monetary(
        compute="_calc_all"
    )
    total_accomodation = fields.Monetary(
        compute="_calc_all"
    )
    total_cleaning = fields.Monetary(
        compute="_calc_all"
    )



    tender_items = fields.One2many(comodel_name="uc.tender.item", inverse_name="tender_id", string="Tender Items",
                                   required=False)
    tender_indirect_stamps = fields.One2many(comodel_name="uc.indirect.stamps", inverse_name="tender_id",
                                             string="Tender Indirect Stamps", required=False)
    tender_indirect_taxes = fields.One2many(comodel_name="uc.indirect.taxes", inverse_name="tender_id",
                                            string="Tender Indirect Taxes", required=False)
    tender_indirect_cars = fields.One2many(comodel_name="uc.indirect.cars", inverse_name="tender_id",
                                           string="Tender Indirect Cars", required=False)
    tender_indirect_travel = fields.One2many(comodel_name="tender.indirect.travel", inverse_name="tender_id",
                                             string="Tender Indirect Travel", required=False)
    tender_indirect_sites = fields.One2many(comodel_name="uc.indirect.sites", inverse_name="tender_id",
                                            string="Tender Indirect Sites Storage Maintenance", required=False)
    tender_indirect_technician = fields.One2many(comodel_name="tender.indirect.sites.technician",
                                                 inverse_name="tender_id", string="Tender Indirect Sites Technician",
                                                 required=False)
    tender_indirect_cleaning = fields.One2many(comodel_name="tender.indirect.sites.cleaning", inverse_name="tender_id",
                                               string="Tender Indirect Sites Cleaning", required=False)
    tender_indirect_accomodation = fields.One2many(comodel_name="uc.indirect.accomodation", inverse_name="tender_id",
                                                   string="Tender Indirect Accomodation", required=False)
    tender_indirect_guard = fields.One2many(comodel_name="uc.indirect.guard", inverse_name="tender_id",
                                            string="Tender Indirect Guard", required=False)
    tender_indirect_other = fields.One2many(comodel_name="uc.indirect.other", inverse_name="tender_id",
                                            string="Tender Indirect Other", required=False)

    tender_items_count = fields.Integer(compute='_compute_tender_items_count', string="Tender Items Count")

    # tender_indirect_stamps = fields.Integer(compute='_compute_tender_indirect_stamps', string="Tender Indirect Stamps")

    def _compute_tender_items_count(self):
        items_data = self.env['uc.tender.item'].read_group(
            [('tender_id', 'in', self.ids), ('display_type', 'not in', ['line_section', 'line_note'])], ['tender_id'],
            ['tender_id'])
        result = dict((data['tender_id'][0], data['tender_id_count']) for data in items_data)
        for tender in self:
            tender.tender_items_count = result.get(tender.id, 0)

    def open_tender_items(self):
        action = self.env["ir.actions.actions"]._for_xml_id("uc_construction.uc_tender_items_act_window")
        action['domain'] = [('tender_id', '=', self.id)]
        action['context'] = {'search_default_items': 1, }

        return action

    @api.depends('tender_indirect_stamps', 'tender_indirect_taxes'
        , 'tender_indirect_other', 'tender_indirect_cars', 'tender_indirect_travel',
                 'tender_indirect_guard', 'tender_indirect_accomodation', 'tender_indirect_technician',
                 'tender_indirect_sites', 'tender_items','tender_indirect_cleaning')
    def _calc_all(self):
        for tender in self:
            print(">>",tender.tender_indirect_stamps)
            tender.stamp_fees = sum(tender.tender_indirect_stamps.mapped('value'))
            tender.taxes_fees = sum(tender.tender_indirect_taxes.mapped('value'))
            tender.other_fees = sum(tender.tender_indirect_other.mapped('otherCostEgy'))
            tender.site_fees = sum(tender.tender_indirect_guard.mapped('guarding_cost_egy')) + \
                               sum(tender.tender_indirect_accomodation.mapped('accomodation_cost_egy')) + \
                               sum(tender.tender_indirect_sites.mapped('total_cost_egy')) + \
                               sum(tender.tender_indirect_cleaning.mapped('total_clearing_cost_eg')) + \
                               sum(tender.tender_indirect_technician.mapped('total_cost_egy'))
            print(">>>",tender.stamp_fees)

            tender.Project_fees = sum(tender.tender_indirect_cars.mapped('car_cost_egy')) + sum(
                tender.tender_indirect_travel.mapped('travel_cost_egy'))

            tender.total_cars= sum(tender.tender_indirect_cars.mapped('car_cost_egy'))
            tender.total_travels= sum(tender.tender_indirect_travel.mapped('travel_cost_egy'))
            tender.total_technician= sum(tender.tender_indirect_technician.mapped('total_cost_egy'))
            tender.total_guard= sum(tender.tender_indirect_guard.mapped('guarding_cost_egy'))
            tender.total_accomodation= sum(tender.tender_indirect_accomodation.mapped('accomodation_cost_egy'))
            tender.total_cleaning= sum(tender.tender_indirect_cleaning.mapped('total_clearing_cost_eg'))

            tender.total_cost = sum(tender.tender_items.mapped('total_cost'))
            tender.consultancy_fees = 0
            tender.total_cost_indirect = tender.stamp_fees + tender.taxes_fees + tender.other_fees + tender.site_fees + tender.Project_fees
            tender.total_cost_direct = sum(tender.tender_items.mapped('total_cost'))
            tender.total_cost_all = tender.total_cost_indirect+tender.total_cost_direct














    default_header_id = fields.Many2one(comodel_name="uc.header", string="Header", compute="_calc_default_header_id",
                                        store=True)

    @api.depends('tender_items.header_id')
    def _calc_default_header_id(self):
        if self.tender_items:
            self.default_header_id = self.tender_items[-1].header_id.id
        else:
            self.default_header_id = self.env.ref('uc_construction.main_header').id
