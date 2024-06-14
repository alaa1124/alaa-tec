from odoo import fields, models, api


class Stage(models.Model):
    _name = 'project.stage'
    _description = 'Stage'

    name = fields.Char(required=1)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)


class contractstage(models.Model):
    _name = "contract.stage"
    stage_id = fields.Many2one("project.stage",string="Stage", )
    prec = fields.Float()
    contract_id = fields.Many2one("project.contract", )

class contractstageline(models.Model):
    _name = "contract.stage.line"
    stage_id = fields.Many2one("project.stage",string="Stage", )
    prec = fields.Float()
    contract_line_id = fields.Many2one("project.contract.line", )