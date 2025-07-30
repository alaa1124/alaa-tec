from odoo import fields, models, api, _

from datetime import datetime

from odoo.exceptions import UserError, ValidationError


class wizard(models.TransientModel):
    _name = "eng.wizard"

    contract_id = fields.Many2one("project.contract", required=True)
    stage_lines = fields.One2many(related='contract_id.stage_lines')
    stage_lines_sub = fields.One2many(related='contract_id.sub_contract_ids.stage_lines')
    eng_id = fields.Many2one("project.engineer.techincal")
    contract_items = fields.Many2many("project.item", "contract_items_lines", "item_id", "id")
    item_ids = fields.Many2many("project.item", "eng_contract_items_lines", "item_id", "id",
                                domain="[('id','in',contract_items)]")

    select_lines = fields.Many2many('project.contract.stage.line', store=True,
                                    domain="['|', ('id', 'in', stage_lines), ('id', 'in', stage_lines_sub)]")

    def save_payment(self):
        # for rec in self.item_ids:
        #     if self.eng_id.type == 'owner':
        #         contract_line = self.env['project.contract.line'] \
        #             .search(
        #             [('state', '=', 'confirm'), ('item', '=', rec.id), '|', ('contract_id', '=', self.contract_id.id),
        #              ('contract_id.parent_contract_id', '=', self.contract_id.id)])
        #     else:
        #         contract_line = self.env['project.contract.line'] \
        #             .search(
        #             [('state', '=', 'confirm'), ('item_sub_id', '=', rec.id), '|',
        #              ('contract_id', '=', self.contract_id.id),
        #              ('contract_id.parent_contract_id', '=', self.contract_id.id)])
        #
        #     for line in contract_line:
        #         if line.display_type == False:
        #             self.create_eng_line(line)

        for line in self.select_lines:
            self.create_eng_line(line)

    def get_previous_amount(self, eng_line):
        previous_amount = 0
        if self.eng_id and eng_line.id and eng_line.stage_id:
            lines = self.env['engineer.techincal.lines'].search(
                [('item', '=', eng_line.item.id), ('related_job_id', '=', eng_line.related_job_id.id),
                 ('stage_id', '=', eng_line.stage_id.id), ('id', '<', eng_line.id), ('eng_id.state', '=', 'confirm'),
                 ('contract_id', '=', self.eng_id.contract_id.id), ('eng_id', '!=', self.eng_id.id)],
                order='stage_id desc')

            previous_amount = sum(lines.mapped('price')) - sum(lines.mapped('previous_amount'))
        return previous_amount

    def create_eng_line(self, line):

        eng_line = self.env['engineer.techincal.lines'].create({
            'eng_id': self.eng_id.id,
            'name': line.name,
            'stage_id': line.stage_id.stage_id.id,
            'stage_prec': line.percent,
            # 'item': line.item.id,
            # 'item_line': line.item_line.id,
            'related_job_id': line.contract_line_id.related_job_id.id,
            'contract_quanity': line.contract_quanity,
            # 'price_unit':(stage.prec/100)*line.price_unit,
            'price_unit': line.price_unit,
            'stage_line': line.id,
        })

        if eng_line:
            # eng_line.previous_amount = eng_line.get_previous_amount(eng_line)
            eng_line.get_previous_qty()

        return eng_line

        # eng_line = ''
        # if line.stage_ids:
        #     for stage in line.stage_ids:
        #         print(">>>>>>>>>>>>>>>.", stage.id)
        #
        #         eng_line = self.env['engineer.techincal.lines'].create({
        #             'eng_id': self.eng_id.id,
        #             'name': line.name,
        #             'stage_id': stage.stage_id.id,
        #             'stage_prec': stage.prec,
        #             'item': line.item.id if self.eng_id.type == 'owner' else line.item_sub_id.id,
        #             'related_job_id': line.related_job_id.id,
        #             'contract_quanity': line.qty,
        #             # 'price_unit':(stage.prec/100)*line.price_unit,
        #             'price_unit': line.price_unit,
        #         })
        #         if eng_line:
        #             eng_line.previous_amount = self.get_previous_amount(eng_line)
        # else:
        #     for stage in line.contract_id.stage_ids:
        #         eng_line = self.env['engineer.techincal.lines'].create({
        #             'eng_id': self.eng_id.id,
        #             'name': line.name,
        #             'stage_id': stage.stage_id.id,
        #             'stage_prec': stage.prec,
        #             'item': line.item.id if self.eng_id.type == 'owner' else line.item_sub_id.id,
        #             'related_job_id': line.related_job_id.id,
        #             'contract_quanity': line.qty,
        #             'price_unit': line.price_unit,
        #             # 'price_unit': (stage.prec / 100) * line.price_unit,
        #         })
        #         if eng_line:
        #             eng_line.previous_amount = self.get_previous_amount(eng_line)
