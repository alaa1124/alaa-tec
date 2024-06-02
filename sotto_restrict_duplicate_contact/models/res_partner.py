# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model_create_multi
    def create(self, values):
        if self.env.company.stop_duplicate_contact and self.env.company.duplicate_contact_fields:
            contact_fields = self.env.company.duplicate_contact_fields
            partner_list = []
            for fields in contact_fields:
                for vals in values:
                    if vals.get(fields.name):
                        partner = self.env['res.partner'].search(
                            [(fields.name, '=', vals.get(fields.name))])
                        if partner:
                            for value in partner:
                                partner_list.append((fields.name, value.name))
            if partner_list:
                message = 'Similiar Value already exists in this partners'
                for partners in partner_list:
                    message += "\n -- %s has same %s" % (
                        partners[1], partners[0])
                raise ValidationError(_(message))
            else:
                return super(ResPartner, self).create(values)
        else:
            return super(ResPartner, self).create(values)

    def write(self, vals):
        if self.env.company.stop_duplicate_contact and self.env.company.duplicate_contact_fields:
            contact_fields = self.env.company.duplicate_contact_fields
            partner_list = []
            for fields in contact_fields:
                if vals.get(fields.name):
                    partner = self.env['res.partner'].search(
                        [(fields.name, '=', vals.get(fields.name))])
                    if partner:
                        for value in partner:
                            partner_list.append((fields.name, value.name))
            if partner_list:
                message = 'Similiar Value already exists in this partners \n'
                for partners in partner_list:
                    message += "\n -- %s has same %s" % (
                        partners[1], partners[0])
                raise ValidationError(_(message))
            else:
                return super(ResPartner, self).write(vals)
        else:
            return super(ResPartner, self).write(vals)
