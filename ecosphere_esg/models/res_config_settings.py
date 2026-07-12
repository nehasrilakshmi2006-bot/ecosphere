from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    esg_notify_compliance_issue = fields.Boolean(
        string='Notify on New Compliance Issue',
        config_parameter='ecosphere_esg.notify_compliance_issue',
        default=True,
    )
    esg_notify_csr_challenge_approval = fields.Boolean(
        string='Notify on CSR/Challenge Approvals',
        config_parameter='ecosphere_esg.notify_csr_challenge_approval',
        default=True,
    )
    esg_notify_policy_acknowledgement = fields.Boolean(
        string='Policy Acknowledgement Reminders',
        config_parameter='ecosphere_esg.notify_policy_acknowledgement',
        default=True,
    )
    esg_notify_badge_unlock = fields.Boolean(
        string='Badge Unlocks',
        config_parameter='ecosphere_esg.notify_badge_unlock',
        default=True,
    )
