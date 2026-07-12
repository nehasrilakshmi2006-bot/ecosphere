from odoo import _, api, fields, models


class EsgPolicyAcknowledgement(models.Model):
    _name = 'esg.policy.acknowledgement'
    _description = 'Policy Acknowledgement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'due_date'

    name = fields.Char(string='Policy', required=True, tracking=True)
    employee_id = fields.Many2one(
        'res.users',
        string='Employee',
        required=True,
        tracking=True,
    )
    due_date = fields.Date(required=True, tracking=True)
    acknowledged = fields.Boolean(default=False, tracking=True)
    acknowledged_date = fields.Date(tracking=True)
    reminder_sent = fields.Boolean(default=False)

    def action_acknowledge(self):
        self.write({
            'acknowledged': True,
            'acknowledged_date': fields.Date.today(),
            'reminder_sent': False,
        })

    @api.model
    def _cron_policy_acknowledgement_reminders(self):
        """Daily cron: schedule activity reminders for overdue acknowledgements."""
        if not self.env['esg.compliance.issue']._is_notification_enabled(
            'ecosphere_esg.notify_policy_acknowledgement'
        ):
            return

        today = fields.Date.today()
        overdue_records = self.search([
            ('acknowledged', '=', False),
            ('due_date', '<', today),
            ('reminder_sent', '=', False),
        ])
        if not overdue_records:
            return

        activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
        if not activity_type:
            return

        for acknowledgement in overdue_records:
            if not acknowledgement.employee_id:
                continue
            acknowledgement.activity_schedule(
                activity_type_id=activity_type.id,
                summary=_('Policy Acknowledgement Overdue'),
                note=_(
                    'Please acknowledge the policy <b>%(policy)s</b>. '
                    'It was due on %(due)s.'
                ) % {
                    'policy': acknowledgement.name,
                    'due': acknowledgement.due_date,
                },
                user_id=acknowledgement.employee_id.id,
                date_deadline=today,
            )
            acknowledgement.message_post(
                body=_(
                    'Automated reminder: policy acknowledgement for <b>%(policy)s</b> '
                    'is overdue (due %(due)s).'
                ) % {
                    'policy': acknowledgement.name,
                    'due': acknowledgement.due_date,
                },
                message_type='notification',
                subtype_xmlid='mail.mt_note',
            )
            acknowledgement.reminder_sent = True
