from odoo import _, fields, models


class EsgCategory(models.Model):
    _name = 'esg.category'
    _description = 'ESG Category'

    name = fields.Char(required=True)
    description = fields.Text()


class EsgChallenge(models.Model):
    _name = 'esg.challenge'
    _description = 'ESG Challenge'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc'

    name = fields.Char(required=True, tracking=True)
    department_id = fields.Many2one('esg.department', string='Department', tracking=True)
    employee_id = fields.Many2one('res.users', string='Employee', tracking=True)
    category_id = fields.Many2one('esg.category', string='ESG Category', tracking=True)
    module = fields.Selection(
        selection=[
            ('environmental', 'Environmental'),
            ('social', 'Social'),
            ('governance', 'Governance'),
        ],
        string='ESG Module',
        required=True,
        tracking=True,
    )
    start_date = fields.Date(string='Start Date', tracking=True)
    end_date = fields.Date(string='End Date', tracking=True)
    status = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('completed', 'Completed'),
        ],
        string='Status',
        default='active',
        tracking=True,
    )
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
        for challenge in self:
            challenge.write({'approval_state': 'approved'})
            challenge._notify_approval_decision(approved=True)
            if challenge.employee_id:
                challenge.employee_id._trigger_eco_streak_update(
                    activity_date=fields.Date.today(),
                    source_model=challenge._name,
                )

    def action_reject(self):
        for challenge in self:
            challenge.write({'approval_state': 'rejected'})
            challenge._notify_approval_decision(approved=False)

    def _notify_approval_decision(self, approved=True):
        self.ensure_one()
        if not self.env['esg.compliance.issue']._is_notification_enabled(
            'ecosphere_esg.notify_csr_challenge_approval'
        ):
            return
        if not self.employee_id or not self.employee_id.partner_id:
            return
        if approved:
            body = _('Your challenge <b>%(name)s</b> has been <b>approved</b>.') % {
                'name': self.name,
            }
            subject = _('Challenge Approved')
        else:
            body = _('Your challenge <b>%(name)s</b> has been <b>rejected</b>.') % {
                'name': self.name,
            }
            subject = _('Challenge Rejected')
        self.message_notify(
            partner_ids=self.employee_id.partner_id.ids,
            body=body,
            subject=subject,
            record_name=self.name,
        )
