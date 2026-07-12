from odoo import api, fields, models


class EsgDepartment(models.Model):
    _name = 'esg.department'
    _description = 'ESG Department'
    _order = 'total_score desc, name'

    name = fields.Char(required=True)
    environmental_score = fields.Float(
        string='Environmental Score',
        default=0.0,
    )
    social_score = fields.Float(
        string='Social Score',
        default=0.0,
    )
    governance_score = fields.Float(
        string='Governance Score',
        default=0.0,
    )
    total_score = fields.Float(
        string='Total Score',
        compute='_compute_total_score',
        store=True,
    )
    rank = fields.Integer(
        string='Rank',
        compute='_compute_rank',
    )

    @api.depends('environmental_score', 'social_score', 'governance_score')
    def _compute_total_score(self):
        for department in self:
            department.total_score = (
                department.environmental_score
                + department.social_score
                + department.governance_score
            )

    def _compute_rank(self):
        ranked_departments = self.search([], order='total_score desc, name')
        rank_map = {
            department.id: index + 1
            for index, department in enumerate(ranked_departments)
        }
        for department in self:
            department.rank = rank_map.get(department.id, 0)
