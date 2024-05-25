# -*- coding: utf-8 -*-
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo.exceptions import UserError,ValidationError

from odoo import api, fields, models
from odoo.tools.translate import _
from datetime import datetime, date
import dateutil.relativedelta
import calendar

class rental_contract(models.Model):
    _name = "rental.contract"
    _description = "Rental Contract"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.depends('loan_line.amount','loan_line.paid')
    def _check_amounts(self):
        total_paid = 0
        total_nonpaid = 0
        amount_total= 0
        for rec in self:
            for line in rec.loan_line:
                amount_total+= line.amount
                if line.paid:
                    total_paid+= line.amount
                else:
                    total_nonpaid+= line.amount

        self.paid = total_paid
        self.balance = total_nonpaid
        self.amount_total=amount_total

    def _voucher_count(self):
        voucher_obj = self.env['account.payment']
        voucher_ids = voucher_obj.search([('real_estate_ref', 'ilike', self.name)])
        self.voucher_count = len(voucher_ids)

    def _entry_count(self):
        move_obj = self.env['account.move']
        move_ids = move_obj.search([('rental_id', 'in', self.ids)])
        self.entry_count = len(move_ids)

    @api.model
    def _get_default_team(self):
        return self.env['crm.team']._get_default_team_id()

    team_id = fields.Many2one('crm.team', 'Sales Channel', change_default=True, default=_get_default_team, oldname='section_id')
    paid= fields.Float(compute='_check_amounts', string='Paid',)
    balance= fields.Float(compute='_check_amounts', string='Balance',)
    amount_total= fields.Float(compute='_check_amounts', string='Total',)
    #rental_contract Info
    name= fields.Char    ('Name', size=64,readonly=True)
    origin= fields.Char    ('Source Document', size=64)
    date_from= fields.Date    ('From Date', required=True)
    date_to= fields.Date    ('To Date', required=True)
    date= fields.Date    ('Date', default=fields.Date.context_today)
    #Building Info
    building= fields.Many2one('building','Building', )
    no_of_floors= fields.Integer ('# Floors')
    building_code= fields.Char    ('Code', size=16)
    #Building Unit Info
    building_unit= fields.Many2one('product.template','Building Unit', required=True,domain=[('is_property', '=', True),('state', '=', 'free')])
    unit_code= fields.Char    ('Code', size=16)
    floor= fields.Char    ('Floor', size=16)
    address= fields.Char    ('Address')
    insurance_fee= fields.Integer   ('Insurance fee', required=True)
    rental_fee= fields.Integer   ('Rental fee', required=True)
    template_id= fields.Many2one('installment.template','Payment Template', )
    type= fields.Many2one('building.type','Building Unit Type', )
    status= fields.Many2one('building.status','Building Unit Status', )
    city= fields.Many2one('cities','City', )
    user_id= fields.Many2one('res.users','Salesman', default=lambda self: self.env.user,)
    partner_id= fields.Many2one('res.partner','Tenant', required=True)
    building_area= fields.Float ('Building Unit Area m²', digits=(12,3))
    loan_line= fields.One2many('loan.line.rs.rent', 'loan_id')
    region= fields.Many2one('regions','Region', )
    country= fields.Many2one('countries','Country', )
    state= fields.Selection([('draft','Draft'),
                             ('confirmed','Confirmed'),
                             ('renew','Renewed'),
                             ('cancel','Canceled'),
                             ], 'State', default=lambda *a: 'draft')
    account_income= fields.Many2one('account.account','Income Account',default=lambda self:self.env['res.config.settings'].browse( self.env['res.config.settings'].search([])[-1].id ).income_account.id if self.env['res.config.settings'].search([]) else "")
    account_analytic_id= fields.Many2one('account.analytic.account', 'Analytic Account',default=lambda self:self.env['res.config.settings'].browse( self.env['res.config.settings'].search([])[-1].id ).analytic_account.id if self.env['res.config.settings'].search([]) else "")
    account_security_deposit= fields.Many2one('account.account', 'Security Deposit Account',default=lambda self:self.env['res.config.settings'].browse( self.env['res.config.settings'].search([])[-1].id ).security_deposit_account.id if self.env['res.config.settings'].search([]) else "")
    voucher_count= fields.Integer('Voucher Count',compute='_voucher_count')
    entry_count= fields.Integer('Entry Count',compute='_entry_count')


    def unlink(self):
        if self.state !='draft':
            raise UserError(_('You can not delete a contract not in draft state'))
        super(rental_contract, self).unlink()

    def view_vouchers(self):
        vouchers=[]
        voucher_obj = self.env['account.payment']
        voucher_ids = voucher_obj.search([('real_estate_ref', '=', self.name)])
        for obj in voucher_ids: vouchers.append(obj.id)

        return {
            'name': _('Receipts'),
            'domain': [('id', 'in', vouchers)],
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model':'account.payment',
            'type':'ir.actions.act_window',
            'nodestroy':True,
            'view_id': False,
            'target':'current',
        }

    def view_entries(self):
        entries=[]
        entry_obj = self.env['account.move']
        entry_ids = entry_obj.search([('rental_id', 'in', self.ids)])
        for obj in entry_ids: entries.append(obj.id)

        return {
            'name': _('Journal Entries'),
            'domain': [('id', 'in', entries)],
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model':'account.move',
            'type':'ir.actions.act_window',
            'nodestroy':True,
            'view_id': False,
            'target':'current',
        }

    def create_move(self,rec,debit,credit,move,account):
        move_line_obj = self.env['account.move.line']
        move_line_obj.create({
            'name': rec.name,
            'partner_id': rec.partner_id.id,
            'account_id': account,
            'debit': debit,
            'credit': credit,
            'move_id': move,
        })

    def generate_cancel_entries(self):
        journal_pool = self.env['account.journal']
        journal = journal_pool.search([('type', '=', 'sale')], limit=1)
        if not journal:
            raise UserError(_('Please set sales accounting journal!'))
        account_move_obj = self.env['account.move']
        total = 0
        for rec in self:
            if not rec.partner_id.property_account_receivable_id:
                raise UserError(_('Please set receivable account for partner!'))
            if not rec.account_income:
                raise UserError(_('Please set income account for this contract!'))
            for line in rec.loan_line:
                total+=line.amount
            account_move_obj.create({'ref' : rec.name, 'journal_id' : journal.id, 'rental_id':rec.id,
                                     'line_ids':[(0,0,{ 'name': rec.name,
                                                        'partner_id': rec.partner_id.id,
                                                        'account_id': rec.partner_id.property_account_receivable_id.id,
                                                        'debit': 0.0,
                                                        'credit': total}),
                                                 (0,0,{'name': rec.name,
                                                       'partner_id': rec.partner_id.id,
                                                       'account_id': rec.account_income.id,
                                                       'debit': total,
                                                       'credit': 0.0})
                                                 ]})

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        if self.filtered(lambda c: c.date_to and c.date_from > c.date_to):
            raise ValidationError(_('Contract start date must be less than contract end date.'))

    def action_confirm(self):
        for contract_obj in self:
            unit = contract_obj.building_unit
            unit.write({'state': 'reserved'})
        self.prepare_lines()
        self.generate_entries()
        self.write({'state':'confirmed'})

    def action_cancel(self):
        for contract_obj in self:
            unit = contract_obj.building_unit
            unit.write({'state':  'free'})
        self.generate_cancel_entries()
        self.write({'state':'cancel'})

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('rental.contract')
        new_id = super(rental_contract, self).create(vals)
        return new_id

    @api.onchange('country')
    def onchange_country(self):
        if self.country:
            city_ids = self.env['cities'].search([('country_id', '=', self.country.id)])
            cities = []
            for u in city_ids: cities.append(u.id)

            return {'domain': {'city': [('id', 'in', cities)]}}

    @api.onchange('city')
    def onchange_city(self):
        if self.city:
            region_ids = self.env['regions'].search([('city_id', '=', self.city.id)])
            regions = []
            for u in region_ids: regions.append(u.id)
            return {'value': {'country':self.city.country_id.id},'domain': {'region': [('id', 'in', regions)]}}

    @api.onchange('region')
    def onchange_region(self):
        if self.region:
            building_ids = self.env['building'].search([('region_id', '=', self.region.id)])
            buildings=[]
            for u in building_ids: buildings.append(u.id)
            return {'value': {'city':self.region.city_id.id},'domain': {'building': [('id', 'in', buildings)]}}

    @api.onchange('building')
    def onchange_building(self):
        if self.building:
            units = self.env['product.template'].search([('is_property', '=', True),('building_id', '=', self.building.id),('state','=','free')])
            unit_ids=[]
            for u in units: unit_ids.append(u.id)
            building_obj = self.env['building'].browse(self.building.id)
            code =  building_obj.code
            no_of_floors =  building_obj.no_of_floors
            region =  building_obj.region_id.id
            if building_obj:
                return {'value': {'building_code': code,
                                  'region':region,
                                  'no_of_floors': no_of_floors},
                        'domain': {'building_unit': [('id', 'in', unit_ids)]}}

    @api.onchange('building_unit')
    def onchange_unit(self):
        self.unit_code = self.building_unit.code
        self.floor = self.building_unit.floor
        # self.pricing = self.building_unit.pricing
        self.type = self.building_unit.ptype.id
        self.address = self.building_unit.address
        self.status = self.building_unit.status.id
        self.building_area = self.building_unit.building_area
        self.building = self.building_unit.building_id.id
        self.region = self.building_unit.region_id.id
        self.country = self.building_unit.country_id.id
        self.city = self.building_unit.city_id.id
        self.rental_fee = self.building_unit.rental_fee
        self.insurance_fee = self.building_unit.insurance_fee


    def generate_entries(self):
        journal_pool = self.env['account.journal']
        journal = journal_pool.search([('type', '=', 'sale')], limit=1)
        if not journal:
            raise UserError(_('Please set sales accounting journal!'))
        account_move_obj = self.env['account.move']
        total = 0
        for rec in self:
            if not rec.partner_id.property_account_receivable_id:
                raise UserError(_('Please set receivable account for partner!'))
            if not rec.account_income:
                raise UserError(_('Please set income account for this contract!'))
            if rec.insurance_fee and not rec.account_security_deposit :
                raise UserError(_('Please set security deposit account for this contract!'))

            for line in rec.loan_line:
                total+=line.amount
            if total <=0:
                raise UserError(_('Invalid Rental Amount!'))
            account_move_obj.create({'ref' : rec.name, 'journal_id' : journal.id, 'rental_id':rec.id,
                                     'line_ids':[(0,0,{ 'name': rec.name,
                                                        'partner_id': rec.partner_id.id,
                                                        'account_id': rec.partner_id.property_account_receivable_id.id,
                                                        'debit': total,
                                                        'credit': 0.0}),
                                                 (0,0,{'name': rec.name,
                                                       'partner_id': rec.partner_id.id,
                                                       'account_id': rec.account_income.id, 'debit': 0.0,
                                                       'credit': (total-rec.insurance_fee),}),
                                                 (0, 0, {'name': rec.name,
                                                         'partner_id': rec.partner_id.id,
                                                         'account_id': rec.account_security_deposit.id, 'debit': 0.0,
                                                         'credit': rec.insurance_fee, })
                                                 ]})
    def subtract_month(self,date, year=0, month=0):
        year, month = divmod(year*12 + month, 12)
        if date.month <= month:
            year = date.year - year - 1
            month = date.month - month + 12
        else:
            year = date.year - year
            month = date.month - month
        return date.replace(year = year, month = month)

    def add_months(self,sourcedate, months):
        month = sourcedate.month - 1 + months
        year = int(sourcedate.year + month / 12 )
        month = month % 12 + 1
        day = min(sourcedate.day,calendar.monthrange(year,month)[1])
        return date(year,month,day)

    def prepare_lines(self):
        rental_lines=[]
        for rec in self:
            i=1
            if rec.insurance_fee > 0:
                rental_lines.append((0,0,{'serial':i,'amount':rec.insurance_fee,'date': rec.date, 'name':_('Insurance Fee')}))
                i+=1
            date_from = rec.date_from
            date_to = rec.date_to
            # date_from=datetime.strptime(date_from, '%Y-%m-%d').date()
            # date_to=datetime.strptime(date_to, '%Y-%m-%d').date()
            loan_date=date_from
            rental_fee = rec.rental_fee
            new_date = date_from
            first_line=True
            while  new_date < date_to:
                new_date = self.add_months(new_date,1)
                if new_date > date_to:# and date_from.month!=date_to.month:
                    new_date = new_date - dateutil.relativedelta.relativedelta(months=1)
                    rental_fee = ((date_to-new_date).days+1)*(float(rental_fee)/30.0)
                    if first_line:
                        rental_lines.append((0,0,{'serial':i,'amount':rental_fee,'date': loan_date, 'name':_('Rental Fee')}))
                        loan_date = self.add_months(loan_date,1)
                        i+=1
                        first_line=False
                    else:
                        rental_lines.append((0,0,{'serial':i,'amount':rental_fee,'date': loan_date, 'name':_('Rental Fee')}))
                        loan_date = self.add_months(loan_date,1)
                        i+=1
                    self.write({'loan_line':rental_lines})
                    return
                else:
                    if first_line:
                        rental_lines.append((0,0,{'serial':i,'amount':rental_fee,'date': loan_date, 'name':_('Rental Fee')}))
                        loan_date = self.add_months(loan_date,1)
                        i+=1
                        first_line=False
                    else:
                        rental_lines.append((0,0,{'serial':i,'amount':rental_fee,'date': loan_date, 'name':_('Rental Fee')}))
                        loan_date = self.add_months(loan_date,1)
                        i+=1
            self.write({'loan_line':rental_lines})

class loan_line_rs_rent(models.Model):
    _name = 'loan.line.rs.rent'
    _order = 'date'

    contract_partner_id= fields.Many2one(related='loan_id.partner_id', string="Partner", store=True)
    contract_building= fields.Many2one(related='loan_id.building', string="Building", store=True)
    contract_building_unit= fields.Many2one(related='loan_id.building_unit', string="Building Unit",domain=[('is_property', '=', True)], store=True)
    date= fields.Date('Due Date')
    name= fields.Char('Name')
    serial= fields.Char('#')
    empty_col= fields.Char(' ',readonly=True)
    amount= fields.Float('Payment', digits=(16, 4))
    paid= fields.Boolean('Paid')
    loan_id= fields.Many2one('rental.contract', '',ondelete='cascade', readonly=True)
    company_id= fields.Many2one('res.company', readonly=True,  default=lambda self: self.env.user.company_id.id)
    contract_user_id= fields.Many2one(string='User', related= 'loan_id.user_id', store=True)


    def send_multiple_installments_rent(self):
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('itsys_real_estate',
                                                         'email_template_installment_notification_rent')[1]
        template_res = self.env['mail.template']
        template = template_res.browse(template_id)
        template.send_mail(self.id, force_send=True)

class accountMove(models.Model):
    _inherit = 'account.move'
    rental_id= fields.Many2one('rental.contract', '',ondelete='cascade', readonly=True)

