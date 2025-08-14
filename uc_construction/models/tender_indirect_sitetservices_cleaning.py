from odoo import models, fields,api

class TenderIndirectSitesCleaning(models.Model):
    _name = 'tender.indirect.sites.cleaning'
    _description = 'this include all the costs of sites technician'
    _rec_name='containers_number'
    company_currency = fields.Many2one("res.currency", string='Currency', default=lambda self:self.env.company.id)
    currency_id = fields.Many2one('res.currency', string='Currency',default=lambda self:self.env.user.company_id.currency_id.id)


    tender_id = fields.Many2one(
        string='Tender',
        comodel_name='uc.tender',
        ondelete='restrict',
    )

    containers_number = fields.Integer(
        string='Number Of  Containers',
    )

    cost_container_clearing = fields.Float(
        string='Cost of Container Clearing',
    )
    total_cost_container_clearing = fields.Monetary(
        string='Total Cost of Container Clearing',compute='_calc_all',store=True
    )

    cost_container_load = fields.Float(
        string='Load Cost per container',
    )
    total_cost_container_load = fields.Monetary(
        string='Total Load Cost per container',compute='_calc_all',store=True
    )
    cost_container_transportation = fields.Float(
        string='Cost per Container Transportatio',
    )
    total_cost_container_transportation = fields.Monetary(
        string='Total  Cost per Container Transportatio',compute='_calc_all',store=True
    )
    cost_container_toll_station = fields.Float(
        string=' Cost Of Toll Station',
    )
    total_cost_container_toll_station = fields.Monetary(
        string=' Total  Cost of  Toll Station',compute='_calc_all',store=True
    )
    cost_container_toll_station_army = fields.Float(
        string=' Cost Of Toll Station Army',
    )

    total_cost_container_toll_station_army = fields.Monetary(
        string='Total Cost of  Toll Station Army',compute='_calc_all',store=True
    )











    storage_days = fields.Integer(
        string='Storage Days',
    )
    storage_cost = fields.Monetary(
        string='Storage Cost', currency_field='currency_id',
    )
    total_storage_cost_port = fields.Monetary(
        string='Total Storage in Port', currency_field='currency_id',compute='_calc_all',store=True
    )

    # MTZ
    other_clear_cost = fields.Float(
        string=' Other Cost',
    )
    #



    demurrages_days = fields.Integer(
        string='Demurrages Days',
    )
    demurrages_cost = fields.Monetary(
        string='Demurrages Cost', currency_field='currency_id',
    )
    total_demurrages_cost = fields.Monetary(
        string='Total Demurrages Cost', currency_field='currency_id',compute='_calc_all',store=True
    )


    #Modified by Moataz
    #Removed
    #total_cost = fields.Monetary(
    #    string='Total Costs', currency_field='currency_id',
    #)
    #total_cost_egy = fields.Monetary(
    #    string='Total Costs in L.E', currency_field='currency_id',compute='_calc_all',store=True
    #)


    unload_days = fields.Integer(
        string='Unload Days',
    )
    unload_cost = fields.Float(
        string='Unload Cost',
    )

    total_unload_cost = fields.Monetary(
        string='Total unload Cost', currency_field='currency_id',compute='_calc_all',store=True
    )



    total_clearing_cost = fields.Monetary(
        string='Total Clearing Cost', currency_field='currency_id',compute='_calc_all',store=True
    )
    total_clearing_cost_eg = fields.Monetary(
        string='Total Clearing Cost in L.E', currency_field='currency_id', compute='_calc_all', store=True
    )
    # Moataz : add other_clear_cost
    @api.depends('containers_number','cost_container_clearing',
                 'cost_container_load',
                 'cost_container_toll_station',
                 'cost_container_toll_station_army',
                 'storage_days',
                 'storage_cost',
                 'demurrages_days',
                 'demurrages_cost',
                 'unload_cost',
                 'unload_days',
                 'other_clear_cost',
                 'currency_id',
                 'cost_container_transportation')
    def _calc_all(self):
        print("::F")
        for item in self:
            item.total_cost_container_clearing=item.containers_number*item.cost_container_clearing
            item.total_cost_container_load=item.containers_number*item.cost_container_load
            item.total_cost_container_transportation=item.containers_number*item.cost_container_transportation
            item.total_cost_container_toll_station=item.containers_number*item.cost_container_toll_station
            item.total_cost_container_toll_station_army=item.containers_number*item.cost_container_toll_station_army
            item.total_demurrages_cost=item.demurrages_days*item.demurrages_cost
            item.total_storage_cost_port=item.storage_days*item.storage_cost
            # item.total_cost=item.total_cost_container_clearing+item.total_cost_container_load+item.total_cost_container_transportation+item.total_cost_container_toll_station+item.total_cost_container_toll_station_army+item.total_demurrages_cost
            item.total_unload_cost=item.unload_days*item.unload_cost
            item.total_clearing_cost=item.total_cost_container_clearing+item.total_cost_container_load + item.total_cost_container_transportation+item.total_cost_container_toll_station + item.total_cost_container_toll_station_army + item.total_demurrages_cost + item.total_unload_cost + item.total_storage_cost_port + item.other_clear_cost

            if item.currency_id.id!=self.env.company.currency_id.id:
                # item.total_cost_egy = item.currency_id._convert(item.total_cost, self.env.company.currency_id, self.env.company,datetime.now().date())
                item.total_clearing_cost_eg = item.currency_id._convert(item.total_clearing_cost, self.env.company.currency_id, self.env.company,datetime.now().date())
            elif item.currency_id.id==self.env.company.currency_id.id:
                # item.total_cost_egy=item.total_cost
                item.total_clearing_cost_eg=item.total_clearing_cost
            else:
                # item.total_cost_egy = 0
                item.total_clearing_cost_eg = 0


