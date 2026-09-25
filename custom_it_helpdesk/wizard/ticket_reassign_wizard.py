from odoo import fields, models


class TicketReassignWizard(models.TransientModel):
    _name = 'ticket.reassign.wizard'
    _description = 'Reassign Ticket Wizard'

    technician_id = fields.Many2one('res.users', string='New Technician', required=True)
    reason = fields.Text(string='Reason for Reassignment', required=True)

    def action_reassign(self):
        ticket_ids = self.env.context.get('active_ids', [])
        if not ticket_ids:
            return {'type': 'ir.actions.act_window_close'}

        tickets = self.env['helpdesk.ticket'].browse(ticket_ids)
        for ticket in tickets:
            ticket.user_id = self.technician_id
            ticket.message_post(
                body=f'Reassigned to {self.technician_id.name}.<br/>Reason: {self.reason}',
                subject='Ticket Reassigned',
            )
        return {'type': 'ir.actions.act_window_close'}
