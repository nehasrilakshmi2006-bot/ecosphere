from odoo import _, fields, models


class EsgCsrActivity(models.Model):
    _name = 'esg.csr.activity'
    _description = 'CSR Activity'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(required=True, tracking=True)
    employee_id = fields.Many2one(
        'res.users',
        string='Employee',
        required=True,
        tracking=True,
    )
    department_id = fields.Many2one('esg.department', string='Department', tracking=True)
    description = fields.Text(tracking=True)
    approval_state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        string='Approval Status',
        default='approved',
        tracking=True,
    )

    def action_submit(self):
        self.write({'approval_state': 'approved'})

    def action_approve(self):
        for activity in self:
            activity.write({'approval_state': 'approved'})
            activity._notify_approval_decision(approved=True)
            if activity.employee_id:
                activity.employee_id._trigger_eco_streak_update(
                    activity_date=fields.Date.today(),
                    source_model=activity._name,
                )

    def action_reject(self):
        for activity in self:
            activity.write({'approval_state': 'rejected'})
            activity._notify_approval_decision(approved=False)

    def _notify_approval_decision(self, approved=True):
        self.ensure_one()
        if not self.env['esg.compliance.issue']._is_notification_enabled(
            'ecosphere_esg.notify_csr_challenge_approval'
        ):
            return
        if not self.employee_id or not self.employee_id.partner_id:
            return
        if approved:
            body = _('Your CSR activity <b>%(name)s</b> has been <b>approved</b>.') % {
                'name': self.name,
            }
            subject = _('CSR Activity Approved')
        else:
            body = _('Your CSR activity <b>%(name)s</b> has been <b>rejected</b>.') % {
                'name': self.name,
            }
            subject = _('CSR Activity Rejected')
        self.message_notify(
            partner_ids=self.employee_id.partner_id.ids,
            body=body,
            subject=subject,
            record_name=self.name,
        )
