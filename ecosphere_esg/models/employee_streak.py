from datetime import timedelta

from odoo import _, api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    current_eco_streak = fields.Integer(
        string='Current Eco Streak',
        default=0,
        tracking=True,
    )
    longest_eco_streak = fields.Integer(
        string='Longest Eco Streak',
        default=0,
        tracking=True,
    )
    last_green_activity_date = fields.Date(
        string='Last Green Activity Date',
        tracking=True,
    )
    eco_points = fields.Integer(
        string='Eco Points',
        default=0,
        tracking=True,
    )
    awarded_streak_milestones = fields.Char(
        string='Awarded Streak Milestones',
        default='',
        copy=False,
        tracking=True,
    )
    next_reward_target = fields.Char(
        string='Next Reward Target',
        compute='_compute_reward_fields',
        store=False,
    )
    days_remaining_to_next_reward = fields.Integer(
        string='Days Remaining Until Next Reward',
        compute='_compute_reward_fields',
        store=False,
    )
    next_reward_progress = fields.Float(
        string='Next Reward Progress',
        compute='_compute_reward_fields',
        store=False,
    )

    @api.depends('current_eco_streak')
    def _compute_reward_fields(self):
        reward_map = {
            3: _('3-Day Streak (+10 Eco Points)'),
            7: _('7-Day Streak (+25 Eco Points)'),
            15: _('Green Warrior Badge'),
            30: _('Eco Champion Badge'),
        }
        for user in self:
            next_milestone = next(
                (milestone for milestone in reward_map if user.current_eco_streak < milestone),
                False,
            )
            if next_milestone:
                user.days_remaining_to_next_reward = max(0, next_milestone - user.current_eco_streak)
                user.next_reward_progress = min(100.0, (user.current_eco_streak / next_milestone) * 100.0)
                user.next_reward_target = reward_map[next_milestone]
            else:
                user.days_remaining_to_next_reward = 0
                user.next_reward_progress = 100.0
                user.next_reward_target = _('All streak rewards unlocked')

    def _trigger_eco_streak_update(self, activity_date=False, source_model=False):
        self.ensure_one()
        if not self:
            return
        activity_date = self._normalize_activity_date(activity_date)
        if not activity_date:
            activity_date = fields.Date.context_today(self)
        if not self.last_green_activity_date:
            self._write_streak_state(activity_date)
            self._apply_streak_rewards(self.current_eco_streak, source_model=source_model)
            return

        last_date = self._normalize_activity_date(self.last_green_activity_date)
        if not last_date:
            self._write_streak_state(activity_date)
            self._apply_streak_rewards(self.current_eco_streak, source_model=source_model)
            return

        if activity_date == last_date:
            return

        if activity_date == (last_date + timedelta(days=1)):
            new_streak = self.current_eco_streak + 1
        else:
            new_streak = 1

        values = {
            'current_eco_streak': new_streak,
            'last_green_activity_date': activity_date,
        }
        if new_streak > self.longest_eco_streak:
            values['longest_eco_streak'] = new_streak
        self.write(values)
        self._apply_streak_rewards(new_streak, source_model=source_model)

    def _write_streak_state(self, activity_date):
        self.ensure_one()
        values = {
            'current_eco_streak': 1,
            'last_green_activity_date': activity_date,
        }
        if 1 > self.longest_eco_streak:
            values['longest_eco_streak'] = 1
        self.write(values)

    def _apply_streak_rewards(self, streak_value, source_model=False):
        self.ensure_one()
        milestone_rewards = [
            {'streak': 3, 'points': 10, 'badge_name': False, 'description': False},
            {'streak': 7, 'points': 25, 'badge_name': False, 'description': False},
            {
                'streak': 15,
                'points': 0,
                'badge_name': 'Green Warrior',
                'description': _('Unlocked for a 15-day eco streak.'),
            },
            {
                'streak': 30,
                'points': 0,
                'badge_name': 'Eco Champion',
                'description': _('Unlocked for a 30-day eco streak.'),
            },
        ]
        awarded = set(filter(None, (self.awarded_streak_milestones or '').split(',')))
        for reward in milestone_rewards:
            if streak_value < reward['streak'] or str(reward['streak']) in awarded:
                continue
            if reward['points']:
                self.write({'eco_points': self.eco_points + reward['points']})
                self._notify_employee(
                    _('Bonus Eco Points Earned'),
                    _(
                        'You earned %(points)s eco points for your %(streak)s-day eco streak.'
                    ) % {
                        'points': reward['points'],
                        'streak': reward['streak'],
                    },
                )
            if reward['badge_name']:
                existing_badge = self.env['esg.badge'].search([
                    ('employee_id', '=', self.id),
                    ('name', '=', reward['badge_name']),
                ], limit=1)
                if existing_badge:
                    if not existing_badge.is_unlocked:
                        existing_badge.action_unlock_badge()
                else:
                    self.env['esg.badge'].create({
                        'name': reward['badge_name'],
                        'employee_id': self.id,
                        'points': 0,
                        'description': reward['description'],
                        'is_unlocked': True,
                        'unlock_date': fields.Date.today(),
                    })
            awarded.add(str(reward['streak']))
        if awarded != set(filter(None, (self.awarded_streak_milestones or '').split(','))):
            self.write({'awarded_streak_milestones': ','.join(sorted(awarded))})

    def _notify_employee(self, subject, body):
        self.ensure_one()
        if not self.partner_id:
            return
        self.env['mail.message'].sudo().create({
            'model': 'res.users',
            'res_id': self.id,
            'subject': subject,
            'body': body,
            'message_type': 'notification',
            'subtype_xmlid': 'mail.mt_note',
            'partner_ids': [(6, 0, self.partner_id.ids)],
        })

    def _notify_streak_expiring(self):
        self.ensure_one()
        self._notify_employee(
            _('Eco Streak Reminder'),
            _('Your eco streak is at risk of expiring tomorrow. Keep your green actions going to protect it.'),
        )

    def _notify_streak_reset(self):
        self.ensure_one()
        self._notify_employee(
            _('Eco Streak Reset'),
            _('Your eco streak has reset to 1 because a day was missed.'),
        )

    @api.model
    def _cron_reset_expired_streaks(self):
        today = fields.Date.from_string(fields.Date.context_today(self))
        yesterday = today - timedelta(days=1)
        users = self.search([
            ('current_eco_streak', '>', 0),
            ('last_green_activity_date', '!=', False),
        ])
        for user in users:
            last_date = user._normalize_activity_date(user.last_green_activity_date)
            if not last_date:
                continue
            if last_date < today:
                user.write({
                    'current_eco_streak': 1,
                    'last_green_activity_date': False,
                })
                user._notify_streak_reset()
            elif last_date == yesterday and user.current_eco_streak > 1:
                user._notify_streak_expiring()

    def _normalize_activity_date(self, activity_date):
        self.ensure_one()
        if not activity_date:
            return False
        if isinstance(activity_date, str):
            return fields.Date.from_string(activity_date)
        return activity_date
