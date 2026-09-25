from odoo import fields, models


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    ticket_ids = fields.One2many(
        'helpdesk.ticket',
        'equipment_id',
        string='Tickets',
    )
