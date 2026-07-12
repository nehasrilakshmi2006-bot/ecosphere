from odoo import _, api, fields, models


class EsgBadge(models.Model):
    _name = 'esg.badge'
    _description = 'ESG Employee Badge'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'unlock_date desc, name'

    name = fields.Char(required=True, tracking=True)
    employee_id = fields.Many2one(
        'res.users',
        string='Employee',
        required=True,
        tracking=True,
    )
    description = fields.Text(tracking=True)
    points = fields.Integer(default=0, tracking=True)
    is_unlocked = fields.Boolean(string='Unlocked', default=False, tracking=True)
    unlock_date = fields.Date(string='Unlock Date', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        badges = super().create(vals_list)
        for badge in badges:
            if badge.is_unlocked:
                badge._notify_badge_unlock()
        return badges

    def action_unlock_badge(self):
        for badge in self:
            if badge.is_unlocked:
                continue
            badge.write({
                'is_unlocked': True,
                'unlock_date': fields.Date.today(),
            })
            badge._notify_badge_unlock()

    def _notify_badge_unlock(self):
        self.ensure_one()
        if not self.env['esg.compliance.issue']._is_notification_enabled(
            'ecosphere_esg.notify_badge_unlock'
        ):
            return
        if not self.employee_id or not self.employee_id.partner_id:
            return
        self.message_notify(
            partner_ids=self.employee_id.partner_id.ids,
            body=_(
                'Congratulations! You unlocked the <b>%(badge)s</b> badge '
                '(%(points)s points).'
            ) % {
                'badge': self.name,
                'points': self.points,
            },
            subject=_('Badge Unlocked'),
            record_name=self.name,
        )
