from odoo import api, fields, models


class EsgAsset(models.Model):
    _name = 'esg.asset'
    _description = 'ESG Asset'

    name = fields.Char(required=True)
    department_id = fields.Many2one('esg.department', string='Department')
    state = fields.Selection(
        selection=[
            ('available', 'Available'),
            ('allocated', 'Allocated'),
        ],
        string='Status',
        default='available',
        required=True,
    )
    booking_ids = fields.One2many('esg.asset.booking', 'asset_id', string='Bookings')
    active_booking_count = fields.Integer(
        string='Active Bookings',
        compute='_compute_booking_counts',
    )

    @api.depends('booking_ids.state')
    def _compute_booking_counts(self):
        for asset in self:
            asset.active_booking_count = len(
                asset.booking_ids.filtered(lambda booking: booking.state == 'active')
            )


class EsgAssetBooking(models.Model):
    _name = 'esg.asset.booking'
    _description = 'ESG Asset Booking'
    _order = 'start_date desc'

    name = fields.Char(required=True)
    asset_id = fields.Many2one(
        'esg.asset',
        string='Asset',
        required=True,
        ondelete='cascade',
    )
    department_id = fields.Many2one(
        related='asset_id.department_id',
        store=True,
        string='Department',
    )
    start_date = fields.Date(required=True, default=fields.Date.today)
    end_date = fields.Date()
    state = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('returned', 'Returned'),
            ('overdue', 'Overdue'),
        ],
        string='Status',
        default='active',
        required=True,
    )

    @api.onchange('end_date')
    def _onchange_end_date(self):
        today = fields.Date.today()
        for booking in self:
            if booking.state == 'active' and booking.end_date and booking.end_date < today:
                booking.state = 'overdue'
