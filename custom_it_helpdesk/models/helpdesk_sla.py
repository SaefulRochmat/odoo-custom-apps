from odoo import fields, models


class HelpdeskSLA(models.Model):
    _name = 'helpdesk.sla'
    _description = 'Helpdesk SLA'
    _order = 'category_id, priority, response_time_hours'

    name = fields.Char(string='SLA Name', required=True)
    category_id = fields.Many2one('helpdesk.category', string='Category', required=True)
    priority = fields.Selection(
        [
            ('0', 'Low'),
            ('1', 'Medium'),
            ('2', 'High'),
            ('3', 'Urgent / Critical'),
        ],
        string='Priority',
        required=True,
        default='1',
    )
    response_time_hours = fields.Float(string='Response Time (Hours)', default=4.0)
    resolution_time_hours = fields.Float(string='Resolution Time (Hours)', default=24.0)

    _sql_constraints = [
        (
            'unique_sla_policy',
            'UNIQUE(category_id, priority)',
            'SLA policy already exists for this category and priority!',
        ),
    ]
