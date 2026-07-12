import base64
import csv
import io

from odoo import _, fields, models
from odoo.exceptions import UserError


class EsgReportWizard(models.TransientModel):
    _name = 'esg.report.wizard'
    _description = 'ESG Report Builder Wizard'

    department_id = fields.Many2one('esg.department', string='Department')
    date_start = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    module = fields.Selection(
        selection=[
            ('environmental', 'Environmental'),
            ('social', 'Social'),
            ('governance', 'Governance'),
        ],
        string='Module',
    )
    employee_id = fields.Many2one('res.users', string='Employee')
    challenge_id = fields.Many2one('esg.challenge', string='Challenge')
    category_id = fields.Many2one('esg.category', string='ESG Category')

    def _validate_date_range(self):
        self.ensure_one()
        if self.date_start and self.date_end and self.date_start > self.date_end:
            raise UserError(_('Start Date must be before or equal to End Date.'))

    def _get_report_lines(self):
        """Build unified report rows from filtered ESG data sources."""
        self.ensure_one()
        self._validate_date_range()
        lines = []

        if not self.module or self.module == 'environmental':
            lines.extend(self._get_environmental_lines())

        if not self.module or self.module == 'social':
            lines.extend(self._get_social_lines())

        if not self.module or self.module == 'governance':
            lines.extend(self._get_governance_lines())

        if self.challenge_id:
            lines = [line for line in lines if line.get('challenge') == self.challenge_id.name]

        if self.category_id:
            lines = [line for line in lines if line.get('category') == self.category_id.name]

        return lines

    def _get_environmental_lines(self):
        CarbonTransaction = self.env['esg.carbon.transaction']
        domain = []
        if self.date_start:
            domain.append(('transaction_date', '>=', self.date_start))
        if self.date_end:
            domain.append(('transaction_date', '<=', self.date_end))

        lines = []
        for transaction in CarbonTransaction.search(domain, order='transaction_date'):
            lines.append({
                'module': 'Environmental',
                'name': transaction.name,
                'date': transaction.transaction_date,
                'department': '',
                'employee': '',
                'category': transaction.emission_factor_id.name or '',
                'challenge': '',
                'value': transaction.total_emissions,
                'details': _('Activity: %(amount)s · Factor: %(factor)s') % {
                    'amount': transaction.activity_amount,
                    'factor': transaction.emission_factor_id.name or 'N/A',
                },
            })
        return lines

    def _get_social_lines(self):
        Department = self.env['esg.department']
        Challenge = self.env['esg.challenge']
        lines = []

        dept_domain = []
        if self.department_id:
            dept_domain.append(('id', '=', self.department_id.id))

        for department in Department.search(dept_domain, order='total_score desc'):
            if self.department_id and department.id != self.department_id.id:
                continue
            lines.append({
                'module': 'Social',
                'name': department.name,
                'date': self.date_end or fields.Date.today(),
                'department': department.name,
                'employee': '',
                'category': 'Department Score',
                'challenge': '',
                'value': department.social_score,
                'details': _('Social pillar score for %(dept)s') % {'dept': department.name},
            })

        challenge_domain = [('module', '=', 'social')]
        if self.date_start:
            challenge_domain.append(('start_date', '>=', self.date_start))
        if self.date_end:
            challenge_domain.append(('end_date', '<=', self.date_end))
        if self.department_id:
            challenge_domain.append(('department_id', '=', self.department_id.id))
        if self.employee_id:
            challenge_domain.append(('employee_id', '=', self.employee_id.id))
        if self.challenge_id:
            challenge_domain.append(('id', '=', self.challenge_id.id))
        if self.category_id:
            challenge_domain.append(('category_id', '=', self.category_id.id))

        for challenge in Challenge.search(challenge_domain, order='start_date'):
            lines.append({
                'module': 'Social',
                'name': challenge.name,
                'date': challenge.start_date,
                'department': challenge.department_id.name or '',
                'employee': challenge.employee_id.name or '',
                'category': challenge.category_id.name or '',
                'challenge': challenge.name,
                'value': 0.0,
                'details': _('Status: %(status)s') % {'status': challenge.status},
            })
        return lines

    def _get_governance_lines(self):
        ComplianceIssue = self.env['esg.compliance.issue']
        Challenge = self.env['esg.challenge']
        domain = []
        if self.date_start:
            domain.append(('due_date', '>=', self.date_start))
        if self.date_end:
            domain.append(('due_date', '<=', self.date_end))
        if self.employee_id:
            domain.append(('owner_id', '=', self.employee_id.id))

        lines = []
        for issue in ComplianceIssue.search(domain, order='due_date'):
            lines.append({
                'module': 'Governance',
                'name': issue.name,
                'date': issue.due_date,
                'department': '',
                'employee': issue.owner_id.name or '',
                'category': 'Compliance Issue',
                'challenge': '',
                'value': 0.0,
                'details': _('Status: %(status)s') % {'status': issue.status},
            })

        challenge_domain = [('module', '=', 'governance')]
        if self.date_start:
            challenge_domain.append(('start_date', '>=', self.date_start))
        if self.date_end:
            challenge_domain.append(('end_date', '<=', self.date_end))
        if self.department_id:
            challenge_domain.append(('department_id', '=', self.department_id.id))
        if self.employee_id:
            challenge_domain.append(('employee_id', '=', self.employee_id.id))
        if self.challenge_id:
            challenge_domain.append(('id', '=', self.challenge_id.id))
        if self.category_id:
            challenge_domain.append(('category_id', '=', self.category_id.id))

        for challenge in Challenge.search(challenge_domain, order='start_date'):
            lines.append({
                'module': 'Governance',
                'name': challenge.name,
                'date': challenge.start_date,
                'department': challenge.department_id.name or '',
                'employee': challenge.employee_id.name or '',
                'category': challenge.category_id.name or '',
                'challenge': challenge.name,
                'value': 0.0,
                'details': _('Status: %(status)s') % {'status': challenge.status},
            })
        return lines

    def action_generate_pdf(self):
        """Trigger the QWeb PDF report via ir.actions.report."""
        self.ensure_one()
        lines = self._get_report_lines()
        if not lines:
            raise UserError(_('No data found for the selected filters.'))
        return self.env.ref('ecosphere_esg.action_report_esg_summary').report_action(self)

    def action_export_excel(self):
        """Export filtered report data to a CSV file (Excel-compatible)."""
        self.ensure_one()
        lines = self._get_report_lines()
        if not lines:
            raise UserError(_('No data found for the selected filters.'))

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'Module', 'Name', 'Date', 'Department', 'Employee',
            'ESG Category', 'Challenge', 'Value', 'Details',
        ])
        for line in lines:
            writer.writerow([
                line.get('module', ''),
                line.get('name', ''),
                line.get('date', '') or '',
                line.get('department', ''),
                line.get('employee', ''),
                line.get('category', ''),
                line.get('challenge', ''),
                line.get('value', 0.0),
                line.get('details', ''),
            ])

        filename = 'ESG_Report_%s.csv' % fields.Date.today()
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(output.getvalue().encode('utf-8-sig')),
            'mimetype': 'text/csv',
            'res_model': self._name,
            'res_id': self.id,
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }
