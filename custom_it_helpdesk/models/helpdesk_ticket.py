from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _description = 'Helpdesk Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, id desc'

    name = fields.Char(
        string='Ticket Number',
        required=True,
        readonly=True,
        default='New',
        copy=False,
        tracking=True,
    )
    title = fields.Char(string='Title', required=True, tracking=True)
    description = fields.Html(string='Description')
    partner_id = fields.Many2one('res.partner', string='Requester', tracking=True)
    user_id = fields.Many2one('res.users', string='Assigned Technician', tracking=True)
    team_leader_id = fields.Many2one('res.users', string='Team Leader', tracking=True)
    category_id = fields.Many2one('helpdesk.category', string='Category', tracking=True)
    stage_id = fields.Many2one(
        'helpdesk.stage',
        string='Stage',
        tracking=True,
        group_expand='_read_group_stage_ids',
        default=lambda self: self._default_stage_id(),
        copy=False,
    )
    priority = fields.Selection(
        [
            ('0', 'Low'),
            ('1', 'Medium'),
            ('2', 'High'),
            ('3', 'Urgent / Critical'),
        ],
        string='Priority',
        default='1',
        required=True,
        tracking=True,
    )
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment')
    sla_id = fields.Many2one('helpdesk.sla', string='SLA Policy')
    sla_deadline = fields.Datetime(string='SLA Deadline')
    sla_reached = fields.Boolean(
        string='Resolved Within SLA',
        compute='_compute_sla_reached',
        store=True,
        tracking=True,
    )
    close_date = fields.Datetime(string='Close Date')
    csat_rating = fields.Selection(
        [
            ('1', '1 - Poor'),
            ('2', '2 - Fair'),
            ('3', '3 - Average'),
            ('4', '4 - Good'),
            ('5', '5 - Excellent'),
        ],
        string='CSAT Rating',
        tracking=True,
    )
    timesheet_ids = fields.One2many(
        'account.analytic.line',
        'ticket_id',
        string='Timesheets',
    )

    _sql_constraints = [
        ('ticket_name_unique', 'UNIQUE(name)', 'Ticket number must be unique!'),
    ]

    @api.model
    def _default_stage_id(self):
        return self.env['helpdesk.stage'].search([('is_starting_stage', '=', True)], limit=1)

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        return self.env['helpdesk.stage'].search([], order='sequence, id')

    @api.model_create_multi
    def create(self, vals_list):
        sequence = self.env['ir.sequence'].search(
            [('code', '=', 'helpdesk.ticket')],
            limit=1,
        )
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                if not sequence:
                    raise UserError(_(
                        'Missing Helpdesk ticket sequence. '
                        'Please configure ir.sequence for code: helpdesk.ticket.'
                    ))
                vals['name'] = sequence.next_by_id()
        return super().create(vals_list)

    @api.onchange('category_id', 'priority')
    def _onchange_category_priority(self):
        if not self.category_id:
            self.sla_id = False
            self.sla_deadline = False
            return

        sla = self.env['helpdesk.sla'].search([
            ('category_id', '=', self.category_id.id),
            ('priority', '=', self.priority or '1'),
        ], limit=1)
        self.sla_id = sla

        if sla:
            if self.create_date:
                now = self.create_date
            else:
                now = fields.Datetime.now()
            response_hours = float(sla.response_time_hours or 0)
            resolution_hours = float(sla.resolution_time_hours or 0)
            self.sla_deadline = now + timedelta(hours=resolution_hours)
        else:
            self.sla_deadline = False

    def action_assign_to_me(self):
        self.ensure_one()
        self.user_id = self.env.user
        return True

    def action_send_csat_survey(self):
        self.ensure_one()
        if not self.partner_id or not self.partner_id.email:
            raise UserError(_('Requester must have a valid email address to send CSAT survey.'))

        template = self.env.ref('custom_it_helpdesk.email_template_helpdesk_csat', raise_if_not_found=False)
        if not template:
            raise UserError(_('CSAT email template is not configured.'))

        template.send_mail(self.id, force_send=True)
        return True

    @api.depends('close_date', 'sla_deadline')
    def _compute_sla_reached(self):
        for record in self:
            record.sla_reached = bool(
                record.close_date
                and record.sla_deadline
                and record.close_date <= record.sla_deadline
            )

    def write(self, vals):
        # Standard closure logic: automatically fill close_date once stage is a closing stage.
        if 'stage_id' in vals:
            stage = self.env['helpdesk.stage'].browse(vals['stage_id'])
            if stage and stage.is_closing_stage:
                vals['close_date'] = vals.get('close_date') or fields.Datetime.now()
        return super().write(vals)
