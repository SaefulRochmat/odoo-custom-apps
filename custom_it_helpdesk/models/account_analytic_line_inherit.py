from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    ticket_id = fields.Many2one(
        'helpdesk.ticket',
        string='Ticket',
        index=True,
        help='The helpdesk ticket associated with this analytical time entry.',
    )
