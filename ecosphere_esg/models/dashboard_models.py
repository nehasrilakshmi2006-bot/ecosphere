from odoo import api, fields, models


class EsgDashboard(models.Model):
    _name = 'esg.dashboard'
    _description = 'ESG Smart Dashboard'

    name = fields.Char(default='ESG Smart Dashboard', required=True)
    assets_available = fields.Integer(
        string='Assets Available',
        compute='_compute_kpis',
    )
    assets_allocated = fields.Integer(
        string='Assets Allocated',
        compute='_compute_kpis',
    )
    active_bookings = fields.Integer(
        string='Active Bookings',
        compute='_compute_kpis',
    )
    overdue_returns = fields.Integer(
        string='Overdue Returns',
        compute='_compute_kpis',
    )
    total_carbon_emissions = fields.Float(
        string='Total Carbon Emissions',
        compute='_compute_kpis',
    )

    def _compute_kpis(self):
        Asset = self.env['esg.asset']
        Booking = self.env['esg.asset.booking']
        Transaction = self.env['esg.carbon.transaction']
        for dashboard in self:
            dashboard.assets_available = Asset.search_count([('state', '=', 'available')])
            dashboard.assets_allocated = Asset.search_count([('state', '=', 'allocated')])
            dashboard.active_bookings = Booking.search_count([('state', '=', 'active')])
            dashboard.overdue_returns = Booking.search_count([('state', '=', 'overdue')])
            dashboard.total_carbon_emissions = sum(
                Transaction.search([]).mapped('total_emissions')
            )
