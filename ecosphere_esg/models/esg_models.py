from odoo import api, fields, models


class EsgEmissionFactor(models.Model):
    _name = 'esg.emission.factor'
    _description = 'ESG Emission Factor'

    name = fields.Char(required=True)
    carbon_value = fields.Float(string='Carbon Value')


class EsgCarbonTransaction(models.Model):
    _name = 'esg.carbon.transaction'
    _description = 'ESG Carbon Transaction'

    name = fields.Char(required=True)
    transaction_date = fields.Date(
        string='Transaction Date',
        default=fields.Date.today,
        required=True,
    )
    activity_amount = fields.Float(string='Activity Amount')
    emission_factor_id = fields.Many2one(
        'esg.emission.factor',
        string='Emission Factor',
    )
    total_emissions = fields.Float(
        string='Total Emissions',
        compute='_compute_total_emissions',
        store=True,
    )

    @api.depends('activity_amount', 'emission_factor_id.carbon_value')
    def _compute_total_emissions(self):
        for record in self:
            carbon_value = (
                record.emission_factor_id.carbon_value
                if record.emission_factor_id
                else 0.0
            )
            record.total_emissions = record.activity_amount * carbon_value



