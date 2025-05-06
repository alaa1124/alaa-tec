from datetime import datetime, timedelta
import time
import calendar
from odoo import api, fields, models
from odoo.tools.translate import _
from datetime import datetime, date, timedelta as td
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta as rd

import logging

_logger = logging.getLogger(__name__)


class ownership_contract(models.Model):
    _name = "ownership.contract"
    _description = "Ownership Contract"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'analytic.mixin']

    def print_installments(self):
        return self.env.ref('itsys_real_estate.unit_installments_report_pdf').report_action(self)

    documents = fields.Many2many('ir.attachment', relation='ownership_att_rel')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('ownership.contract')
        new_id = super(ownership_contract, self).create(vals)
        return new_id

    @api.model
    def _get_default_currency(self):
        return self.env.company.currency_id.id

    interest_rate = fields.Float(string='Interest Rate (%)', digits='Product Price')
    loan_amount = fields.Float(string='Loan Amount', digits='Product Price')
    mortgage_insurance = fields.Float(string='Mortgage Insurance', digits='Product Price')
    home_insurance = fields.Float(string='Home Insurance', digits='Product Price')
    hoa = fields.Float(string='HOA', digits='Product Price')
    property_tax = fields.Float(string='Property Tax', digits='Product Price')
    principal_interest = fields.Float(string='Principal & Interest', digits='Product Price')
    monthly_payment = fields.Float(string='Monthly Payment', digits='Product Price')
    advance_payment = fields.Float(string='Down Payment', digits='Product Price')
    advance_payment_percent = fields.Float(string='%', digits='Product Price')
    pricing = fields.Integer('Home Pricing', related='building_unit.pricing', digits='Product Price', store=True)
    currency_id = fields.Many2one('res.currency', store=True, readonly=True, tracking=True, required=True,
                                  string='Currency', default=_get_default_currency)
    entry_count = fields.Integer('Entry Count', compute='_entry_count')
    check_count = fields.Integer('Entry Count', compute='_entry_count')

    paid = fields.Float(compute='_check_amounts', string='Paid', store=True)
    balance = fields.Float(compute='_check_amounts', string='Balance', store=True)
    total_amount = fields.Float(compute='_check_amounts', string='Total Amount', store=True)
    total_npv = fields.Float(compute='_check_amounts', string='NPV', store=True)
    # ownership_contract Info
    name = fields.Char('Name', size=64, readonly=True)
    reservation_id = fields.Many2one('unit.reservation', 'Reservation')
    date = fields.Date('Date', required=True, default=fields.Date.context_today)
    date_payment = fields.Date('First Payment Date', required=True)
    # Building Info
    building = fields.Many2one('building', 'Building')
    no_of_floors = fields.Integer('# Floors')
    building_code = fields.Char('Code', size=16)
    # Building Unit Info
    building_unit = fields.Many2one('product.template', 'Building Unit',
                                    domain=[('is_property', '=', True), ('state', '=', 'free')], required=True)
    rplc_building_unit = fields.Many2one('product.template', 'New Building Unit',
                                         domain=[('is_property', '=', True), ('state', '=', 'free')])
    unit_code = fields.Char('Code', size=16)
    floor = fields.Char('Floor', size=16)
    address = fields.Char('Address')
    origin = fields.Char('Source Document')
    template_id = fields.Many2one('installment.template', 'Payment Template', required=False)
    type = fields.Many2one('building.type', 'Building Unit Type')
    status = fields.Many2one('building.status', 'Building Unit Status')
    city = fields.Many2one('cities', 'City')
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user, )
    partner_id = fields.Many2one('res.partner', 'Partner', required=True)
    building_area = fields.Float('Building Unit Area m²', digits=(12, 3))
    loan_line = fields.One2many('loan.line.rs.own', 'loan_id')
    region = fields.Many2one('regions', 'Region')
    country = fields.Many2one('countries', 'Country')
    state = fields.Selection([('draft', 'Reservation'),
                              ('confirmed', 'Contract'),
                              ('cancel', 'Canceled'),
                              ], 'State', default='draft')

    voucher_count = fields.Integer('Voucher Count', compute='_voucher_count')
    account_income = fields.Many2one('account.account', 'Income Account',
                                     default=lambda self: self.env['res.config.settings'].browse(
                                         self.env['res.config.settings'].search([])[-1].id).income_account.id if
                                     self.env['res.config.settings'].search([]) else "")
    account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account',
                                          default=lambda self: self.env['res.config.settings'].browse(
                                              self.env['res.config.settings'].search([])[-1].id).analytic_account.id if
                                          self.env['res.config.settings'].search([]) else "")
    old_contract = fields.Many2one('ownership.contract', 'Old Contract', )

    # Installments fields
    adv_pay = fields.Integer(string='Adv. Payment %', default=25, help="Advance payment percent ex. 25")
    handover_inst = fields.Integer(string='Handover installment %', default=10,
                                   help="Handover installment amount in percent ex. 10")
    handover_seq = fields.Integer(string='Handover Sequence', default=8,
                                  help="Sequence of handover installment ex. 8th installment")
    month_count = fields.Integer(string='Inst. Plan Duration months', default=120,
                                 help="Installment Plan Duration or Total number of months \n ex. 120 months / 10 years")
    inst_count = fields.Integer(string='Installments count', default=40,
                                help="Total number of intallments \n ex. 40 means every 3 months for the 120 months plan")
    active = fields.Boolean('Active', default=True, tracking=True)

    @api.constrains('total_amount')
    def check_total_amount(self):
        for rec in self:
            if not rec.loan_line:
                continue
            if rec.total_amount != rec.pricing:
                raise ValidationError(f'Total Amount must be {rec.pricing} the same as Home Pricing. Difference is {rec.pricing - rec.total_amount}')

    def action_draft(self):
        self.write({'state': 'draft'})

    def replace_unit(self):
        adv_pay = (100 * self.paid) / self.rplc_building_unit.pricing
        vals = {
            'partner_id': self.partner_id.id,
            'building_unit': self.rplc_building_unit.id,
            'date_payment': fields.Date.today(),
            'old_contract': self.id,
            'month_count': self.month_count,
            'inst_count': self.inst_count,
            'adv_pay': adv_pay,
            'handover_inst': self.handover_inst,
            'handover_seq': self.handover_seq,
        }
        new_contract = self.env['ownership.contract'].create(vals)
        self.action_cancel()
        return {
            'name': _('Contracts'),
            'type': 'ir.actions.act_window',
            'res_id': new_contract.id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ownership.contract',
        }

    @api.constrains('partner_id')
    def set_unit_reservation(self):
        self.building_unit.partner_id = self.partner_id
        self.building_unit.state = self.partner_id and 'reserved' or 'free'
        self.building_unit.reservation_date = self.partner_id and self.create_date or None
        self.building_unit.reservation_end_date = self.create_date and self.create_date + timedelta(days=1) or None

    @api.onchange(
        'building_unit',
        'adv_pay',
        'month_count',
        'inst_count',
        'handover_inst',
        'handover_seq',
    )
    @api.constrains(
        'building_unit',
        'adv_pay',
        'month_count',
        'inst_count',
        'handover_inst',
        'handover_seq',
    )
    def update_lines(self):
        self.loan_line = None

    def update_inst_lines(self):
        self.loan_line = None
        self._cr.commit()
        loan_lines = self.compute_installments()
        total_npv = sum(l[2]['npv'] for l in loan_lines)
        npv = (100 * total_npv) / self.pricing
        if npv < 10:
            raise UserError(f''' {npv}
            The Plan is invalid, Try to adjust it using below points:\n
            - Increase "Adv. Payment" or "Handover Inst." or "Inst. Count"\n
            - Reduce "Total # of Months" or "handover sequence"
            ''')
        else:
            self.loan_line = loan_lines

    def compute_installments(self):
        npv = float(self.env['ir.config_parameter'].sudo().get_param('itsys_real_estate.npv')) / 100
        # _logger.error(f'>>>>>>>>>>>>>>>> NPV: {npv}')
        inst_lines = []
        name = self.name or 'new'
        inst_count = self.inst_count or 0
        amount = self.pricing or 0
        start_date = self.date_payment or date.today()
        adv_pay = amount * (self.adv_pay / 100 or 0 / 100)
        handover_inst = amount * (self.handover_inst / 100 or 0 / 100)
        inst_count = self.inst_count  # > 0 and self.inst_count or 1
        month_count = self.month_count  # > 0 and self.month_count or 1
        rem_inst_amount = amount - adv_pay - handover_inst
        # g1_inst_amount = (rem_inst_amount*0.67) / round(inst_count/2)
        # g2_inst_amount = (rem_inst_amount*0.33) / round(inst_count/2)

        # g1_inst_amount = (rem_inst_amount*0.60) / round(inst_count/2)
        # g2_inst_amount = (rem_inst_amount*0.40) / round(inst_count/2)

        g_inst_amount = rem_inst_amount * 0.5 / round(inst_count / 2)
        print('g_inst_amount', g_inst_amount)
        if inst_count % 2 > 0:
            inst_count += 1
            # self.inst_count = inst_count
            # self._cr.commit()

        inst_months = round(month_count / inst_count)
        # self.inst_count = month_count / inst_months

        if self.handover_seq > int(inst_count / 2):
            raise UserError(f"Handover Sequence max is {int(inst_count / 2)}.")
        # if self.handover_inst + self.adv_pay < 30:
        #     raise UserError('Adv. Payment + Handover Payment must be at least 30%')
        inst_lines.append(
            (0, 0, {
                'number': (name + ' / ' + 'advance payment'),
                'amount': adv_pay,
                'date': start_date,
                'name': 'Advance Payment',
                'npv': adv_pay,
                'analytic_distribution': self.analytic_distribution,
            }),
        )
        if self.handover_seq:
            irng = range(1, int(inst_count) + 2)
        else:
            irng = range(1, int(inst_count) + 1)

        # print('irng', irng)
        for ili in irng:
            iseq = ili
            mns = iseq * inst_months
            idate = start_date + rd(months=mns)
            amount = 0
            # name = f'Inst # {str(iseq)} / {mns} months'
            # if iseq <= (len(irng)/2)+1:
            #     amount = g1_inst_amount
            # else:
            #     amount = g2_inst_amount

            amount = g_inst_amount

            if iseq == self.handover_seq:
                mns = iseq * inst_months
                amount = handover_inst
                name = f'{mns} months (Handover)'
            elif iseq < self.handover_seq:
                mns = iseq * inst_months
                name = f'Inst # {str(iseq)} / {mns} months'

            elif iseq > self.handover_seq and self.handover_seq > 0:
                iseq = iseq - 1
                mns = iseq * inst_months
                name = f'Inst # {str(iseq)} / {mns} months'

            elif self.handover_seq == 0:
                iseq = iseq
                mns = iseq * inst_months
                name = f'Inst # {str(iseq)} / {mns} months'

            # print('npv', npv)
            # print('amount', amount)
            inpv = amount / (1 + (npv / 12)) ** mns
            # print('name', self.name)
            inst_lines.append(
                (0, 0, {
                    'number': (self.name + ' / ' + str(iseq)),
                    'amount': amount,
                    'date': idate,
                    'name': name,
                    'npv': inpv,
                    'analytic_distribution': self.analytic_distribution,
                }),
            )

        return inst_lines

    def _prepare_lines(self, first_date):
        pricing = self.pricing
        loan_lines = []
        if self.template_id:
            ind = 1
            mon = self.template_id.duration_month
            yr = self.template_id.duration_year
            repetition = self.template_id.repetition_rate
            advance_percent = self.template_id.adv_payment_rate
            deduct = self.template_id.deduct
            if not first_date:
                raise UserError(_('Please select first payment date!'))
            # first_date=datetime.strptime(first_date, '%Y-%m-%d').date()
            adv_payment = pricing * float(advance_percent) / 100
            if mon > 12:
                x = mon / 12
                mon = (x * 12) + mon % 12
            mons = mon + (yr * 12)
            if adv_payment:
                loan_lines.append((0, 0,
                                   {'number': (self.name + ' - ' + str(ind)), 'amount': adv_payment, 'date': first_date,
                                    'name': _('Advance Payment')}))
                ind += 1
                if deduct:
                    pricing -= adv_payment
            loan_amount = (pricing / float(mons)) * repetition
            m = 0
            while m < mons:
                loan_lines.append((0, 0,
                                   {'number': (self.name + ' - ' + str(ind)), 'amount': loan_amount, 'date': first_date,
                                    'name': _('Loan Installment')}))
                ind += 1
                first_date = self.add_months(first_date, repetition)
                m += repetition
        return loan_lines

    def _entry_count(self):
        move_obj = self.env['account.move']
        move_ids = move_obj.search([('ownership_id', 'in', self.ids)])
        checks = self.env['account.payment'].search([('ownership_line_id', 'in', self.loan_line.ids)])
        self.entry_count = len(move_ids)
        self.check_count = len(checks)

    def view_entries(self):
        entries = []
        entry_obj = self.env['account.move']
        entry_ids = entry_obj.search([('ownership_id', 'in', self.ids)])
        for obj in entry_ids: entries.append(obj.id)

        return {
            'name': _('Journal Entries'),
            'domain': [('id', 'in', entries)],
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'view_id': False,
            'target': 'current',
        }

    @api.depends('loan_line.npv', 'loan_line.amount', 'loan_line.total_paid_amount', 'loan_line')
    def _check_amounts(self):
        total_paid = 0
        total_npv = 0
        total = 0
        for rec in self:
            for line in self.loan_line:
                total_paid += line.total_paid_amount
                total += line.amount
                total_npv += line.npv

            price = rec.pricing or 1
            rec.paid = total_paid
            rec.balance = (total - total_paid)
            rec.total_amount = total
            rec.total_npv = (100 * total_npv) / price

    def _voucher_count(self):
        voucher_obj = self.env['account.payment']
        voucher_ids = voucher_obj.search([('real_estate_ref', '=', self.name)])
        self.voucher_count = len(voucher_ids)

    @api.onchange('interest_rate', 'pricing', 'advance_payment_percent', 'property_tax', 'hoa', 'advance_payment',
                  'home_insurance', 'mortgage_insurance')
    def onchange_mortgage(self):
        if self.pricing:
            monthly_int = self.interest_rate / 100 / 12
            self.advance_payment = self.pricing * self.advance_payment_percent / 100.0
            self.loan_amount = self.pricing - self.advance_payment
            d = (1 - ((1 + monthly_int) ** 360))

            if d:
                self.principal_interest = (self.loan_amount * monthly_int) / d
            self.monthly_payment = self.principal_interest + self.property_tax + self.hoa + self.home_insurance + self.mortgage_insurance

    def unlink(self):
        if self.state != 'draft':
            raise UserError(_('You can not delete a contract not in draft state'))
        else:
            if self.building_unit:
                self.building_unit.write({
                    'state': 'free',
                    'partner_id': False,
                })
        super(ownership_contract, self).unlink()

    def view_vouchers(self):
        vouchers = []
        voucher_obj = self.env['account.payment']
        voucher_ids = voucher_obj.search([('real_estate_ref', '=', self.name)])
        for obj in voucher_ids: vouchers.append(obj.id)

        return {
            'name': _('Receipts'),
            'domain': [('id', 'in', vouchers)],
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'view_id': False,
            'target': 'current',
        }

    def unit_status(self):
        return self.building_unit.state

    def action_confirm(self):
        unit = self.building_unit
        unit.write({
            'state': 'sold',
            'partner_id': self.partner_id.id,
        })
        self.write({'state': 'confirmed'})
        self.generate_entries()

    def action_cancel(self):
        unit = self.building_unit
        unit.write({'state': 'free', 'partner_id': False, })
        self.generate_cancel_entries()
        self.write({'state': 'cancel'})

    # @api.onchange('country')
    def onchange_country(self):
        if self.country:
            city_ids = self.env['cities'].search([('country_id', '=', self.country.id)])
            cities = []
            for u in city_ids: cities.append(u.id)

            return {'domain': {'city': [('id', 'in', cities)]}}

    # @api.onchange('city')
    def onchange_city(self):
        if self.city:
            region_ids = self.env['regions'].search([('city_id', '=', self.city.id)])
            regions = []
            for u in region_ids: regions.append(u.id)
            return {'value': {'country': self.city.country_id.id}, 'domain': {'region': [('id', 'in', regions)]}}

    # @api.onchange('region')
    def onchange_region(self):
        if self.region:
            building_ids = self.env['building'].search([('region_id', '=', self.region.id)])
            buildings = []
            for u in building_ids: buildings.append(u.id)
            return {'value': {'city': self.region.city_id.id}, 'domain': {'building': [('id', 'in', buildings)]}}

    # @api.onchange('building')
    def onchange_building(self):
        if self.building:
            units = self.env['product.template'].search(
                [('is_property', '=', True), ('building_id', '=', self.building.id), ('state', '=', 'free')])
            unit_ids = []
            for u in units: unit_ids.append(u.id)
            building_obj = self.env['building'].browse(self.building.id)
            code = building_obj.code
            no_of_floors = building_obj.no_of_floors
            region = building_obj.region_id.id
            if building_obj:
                return {'value': {'building_code': code,
                                  'region': region,
                                  'no_of_floors': no_of_floors},
                        'domain': {'building_unit': [('id', 'in', unit_ids)]}}

    def add_months(self, sourcedate, months):
        month = sourcedate.month - 1 + months
        year = int(sourcedate.year + month / 12)
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    # @api.onchange('building_unit')
    def onchange_unit(self):
        self.unit_code = self.building_unit.code
        self.floor = self.building_unit.floor
        self.pricing = self.building_unit.pricing
        self.type = self.building_unit.ptype
        self.address = self.building_unit.address
        self.status = self.building_unit.status
        self.building_area = self.building_unit.building_area
        self.building = self.building_unit.building_id.id
        self.region = self.building_unit.region_id.id
        self.country = self.building_unit.country_id.id
        self.city = self.building_unit.city_id.id

    # @api.onchange('reservation_id')
    def onchange_reservation(self):
        self.building = self.reservation_id.building.id
        self.city = self.reservation_id.city.id
        self.region = self.reservation_id.region.id
        self.building_code = self.reservation_id.building_code
        self.partner_id = self.reservation_id.partner_id.id
        self.building_unit = self.reservation_id.building_unit.id
        self.unit_code = self.reservation_id.unit_code
        self.address = self.reservation_id.address
        self.floor = self.reservation_id.floor
        self.building_unit = self.reservation_id.building_unit.id
        self.pricing = self.reservation_id.pricing
        self.date_payment = self.reservation_id.date_payment
        self.template_id = self.reservation_id.template_id.id
        self.type = self.reservation_id.type
        self.status = self.reservation_id.status
        self.building_area = self.reservation_id.building_area
        if self.template_id:
            loan_lines = self._prepare_lines(self.date_payment)
            self.loan_line = loan_lines

    def create_move(self, rec, debit, credit, move, account):
        move_line_obj = self.env['account.move.line']
        move_line_obj.create({
            'name': rec.name,
            'partner_id': rec.partner_id.id,
            'account_id': account,
            'debit': debit,
            'credit': credit,
            'move_id': move,
        })

    cheque_no = fields.Integer(string='1st Cheque #')
    cheque_bank = fields.Many2one('res.bank', string='Cheques Bank')
    cheque_acc_id = fields.Many2one('account.account', string='Cheques Account')
    journal_id = fields.Many2one('account.journal', domain="[('cheque_recieve','=',True)]")

    def unit_cheques(self):
        action = self.env["ir.actions.act_window"]._for_xml_id('check_management.action_payment_account')
        action['domain'] = [('ownership_contract', '=', self.id), ('is_cheque', '=', True)]
        return action

    def create_cheques(self):

        if self.check_count > 0:
            raise UserError('Cheques are already created')

        for rec in self:
            # if not rec.partner_id.property_account_receivable_id:
            #     raise UserError(_('Please set receivable account for partner!'))

            cheque_no = self.cheque_no
            for line in rec.loan_line.filtered(lambda l: l.amount > 0):
                self.env['account.payment'].create({
                    'type_cheq': 'recieve_chq',
                    'payment_type': 'inbound',
                    'is_cheque': True,
                    'partner_id': self.partner_id.id,
                    'cheque_bank': self.cheque_bank.id,
                    'cheque_no': cheque_no,
                    'journal_cheque': self.journal_id.id,
                    'amount': line.amount,
                    'date': date.today(),
                    'effective_date': line.date,
                    'ownership_line_id': line.id,
                })

                cheque_no += 1

    def generate_entries(self):
        journal_pool = self.env['account.journal']
        journal = journal_pool.search([('type', '=', 'sale')], limit=1)
        if not journal:
            raise UserError(_('Please set sales accounting journal!'))
        account_move_obj = self.env['account.move']
        for rec in self:
            unit = rec.building_unit
            rec.account_income = unit.property_account_income_id or unit.categ_id.property_account_income_categ_id
            amls = []
            if not rec.partner_id.property_account_receivable_id:
                raise UserError(_('Please set receivable account for partner!'))
            if not rec.account_income:
                raise UserError(_('Please set income account for this contract!'))

            for line in rec.loan_line:
                amls.append((0, 0, {
                    'name': line.name,
                    'partner_id': rec.partner_id.id,
                    'account_id': rec.partner_id.property_account_receivable_id.id,
                    'date_maturity': line.date,
                    'debit': round(line.amount, 2),
                    'credit': 0.0,
                    'analytic_distribution': self.analytic_distribution
                }))

            amls.append((0, 0, {
                'name': rec.name,
                'partner_id': rec.partner_id.id,
                'account_id': rec.account_income.id,
                'debit': 0.0,
                'credit': round(sum(a[2]['debit'] for a in amls), 2),
                'analytic_distribution': self.analytic_distribution
            }))

            am = account_move_obj.create({
                'ref': rec.name,
                'journal_id': journal.id,
                'ownership_id': rec.id,
                'line_ids': amls,
            })

            am.action_post()

    def generate_cancel_entries(self):
        # ToDo: reverse JE
        return True


class loan_line_rs_own(models.Model):
    _name = 'loan.line.rs.own'
    _inherit = ['analytic.mixin']
    _order = 'date'

    def view_payments(self):
        payments = self.env['account.payment'].sudo().search([('ownership_line_id', '=', self.id)]).ids
        return {
            'name': _('Vouchers'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', payments)],
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
        }

    def _count_payment(self):
        for rec in self:
            payments = self.env['account.payment'].sudo().search([('ownership_line_id', '=', rec.id)]).ids
            rec.payment_count = len(payments)

    @api.model
    def create(self, vals):
        vals['number'] = self.env['ir.sequence'].get('loan.line.rs.own')
        new_id = super(loan_line_rs_own, self).create(vals)
        return new_id

    @api.depends('amount', 'total_paid_amount')
    def _check_amounts(self):
        for rec in self:
            rec.total_remaining_amount = rec.amount - rec.total_paid_amount

    cancelled = fields.Boolean('Cancelled')
    number = fields.Char('Number')

    contract_user_id = fields.Many2one(string='User', related='loan_id.user_id', store=True)
    contract_partner_id = fields.Many2one(string='Partner', related='loan_id.partner_id', store=True)
    contract_building = fields.Many2one(string="Building", related='loan_id.building', store=True)
    contract_building_unit = fields.Many2one(related='loan_id.building_unit', string="Building Unit", store=True,
                                             domain=[('is_property', '=', True)])
    contract_city = fields.Many2one(related='loan_id.city', string="City", store=True)
    contract_region = fields.Many2one(related='loan_id.region', string="Region", store=True)
    contract_country = fields.Many2one(related='loan_id.country', string="Country", store=True)
    date = fields.Date('Due Date')
    name = fields.Char('Name')
    empty_col = fields.Char(' ', readonly=True)

    amount = fields.Float('Payment', digits=(16, 4), )
    npv = fields.Float('NPV', digits=(16, 4), )
    total_paid_amount = fields.Float('Paid Amount', digits=(16, 4))
    total_remaining_amount = fields.Float(compute='_check_amounts', string='Due Amount', digits=(16, 4), store=True)

    loan_id = fields.Many2one('ownership.contract', '', ondelete='cascade', readonly=True)
    status = fields.Char('Status')
    company_id = fields.Many2one('res.company', readonly=True, default=lambda self: self.env.user.company_id.id)

    payment_count = fields.Integer(compute='_count_payment', string='# Counts')

    def send_multiple_installments(self):
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('itsys_real_estate',
                                                         'email_template_installment_notification')[1]
        template_res = self.env['mail.template']
        template = template_res.browse(template_id)
        template.send_mail(self.id, force_send=True)


class AccountMove(models.Model):
    _inherit = 'account.move'
    ownership_id = fields.Many2one('ownership.contract', 'Unit Contract', ondelete='cascade', readonly=True)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    ownership_id = fields.Many2one(
        'ownership.contract', 'Unit Contract', related="move_id.ownership_id",
        ondelete='cascade', readonly=True, store=True,
    )

    unit_id = fields.Many2one(
        'product.template', 'Unit RS', related="move_id.ownership_id.building_unit",
        ondelete='cascade', readonly=True, store=True,
    )
