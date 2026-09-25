from odoo import fields, models


class HelpdeskCategory(models.Model):
    _name = 'helpdesk.category'
    _description = 'Helpdesk Category'
    _order = 'name'

    name = fields.Char(string='Category Name', required=True, translate=True)
    code = fields.Char(string='Code', required=True)
    default_technician_id = fields.Many2one(
        'res.users',
        string='Default Technician',
        help='Technician assigned automatically when this category is selected.',
    )

    _sql_constraints = [
        ('unique_category_code', 'UNIQUE(code)', 'Category code must be unique!'),
    ]
