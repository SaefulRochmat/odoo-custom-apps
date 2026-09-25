from odoo import fields, models


class HelpdeskStage(models.Model):
    _name = 'helpdesk.stage'
    _description = 'Helpdesk Stage'
    _order = 'sequence, id'

    name = fields.Char(string='Stage Name', required=True, translate=True)
    sequence = fields.Integer(string='Sequence', default=10)
    is_starting_stage = fields.Boolean(string='Starting Stage', default=False)
    is_closing_stage = fields.Boolean(string='Closing Stage', default=False)
    fold = fields.Boolean(string='Folded in Kanban', default=False)
