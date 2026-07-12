from odoo import _, api, fields, models


class EsgComplianceIssue(models.Model):
    _name = 'esg.compliance.issue'
    _description = 'ESG Compliance Issue'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True, tracking=True)
    description = fields.Text(tracking=True)
    owner_id = fields.Many2one('res.users', string='Owner', tracking=True)
    due_date = fields.Date(string='Due Date', tracking=True)
    status = fields.Selection(
        selection=[
            ('open', 'Open'),
            ('resolved', 'Resolved'),
            ('overdue', 'Overdue'),
        ],
        string='Status',
        default='open',
        tracking=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        issues = super().create(vals_list)
        if self._is_notification_enabled('ecosphere_esg.notify_compliance_issue'):
            for issue in issues:
                issue._notify_owner_new_issue()
        return issues

    @api.model
    def _is_notification_enabled(self, config_key):
        return (
            self.env['ir.config_parameter'].sudo().get_param(config_key, 'False')
            == 'True'
        )

    def _notify_owner_new_issue(self):
        self.ensure_one()
        if not self.owner_id or not self.owner_id.partner_id:
            return
        self.message_notify(
            partner_ids=self.owner_id.partner_id.ids,
            body=_(
                'A new compliance issue <b>%(name)s</b> has been assigned to you. '
                'Due date: %(due)s'
            ) % {
                'name': self.name,
                'due': self.due_date or _('Not set'),
            },
            subject=_('New Compliance Issue Assigned'),
            record_name=self.name,
        )
