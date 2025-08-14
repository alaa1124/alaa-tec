from odoo import api, fields, models,_
from odoo.exceptions import ValidationError


class Header(models.Model):
    _name='uc.header'
    name = fields.Char(string="Name", required=True)


    def unlink(self):
        for rec in self:
            if rec.id == self.env.ref('uc_construction.main_header') :
                raise ValidationError(_('Not Allow Delete This Record!'))
        return super(Header, self).unlink()



