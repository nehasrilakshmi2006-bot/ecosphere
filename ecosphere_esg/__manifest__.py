{
    'name': 'EcoSphere ESG',
    'version': '18.0.4.0.0',
    'category': 'Sustainability',
    'summary': 'ESG Management Platform',
    'description': """
        ESG Management Platform for tracking carbon emissions,
        emission factors, compliance issues, department rankings,
        smart sustainability dashboards, custom report builder,
        and automated notification engine.
    """,
    'author': 'EcoSphere',
    'depends': ['base', 'web', 'mail', 'board'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron_jobs.xml',
        'reports/esg_report_template.xml',
        'reports/esg_report_actions.xml',
        'data/demo_data.xml',
        'views/esg_views.xml',
        'views/department_views.xml',
        'views/dashboard_views.xml',
        'views/esg_dashboard_views.xml',
        'views/notification_views.xml',
        'views/res_config_settings_views.xml',
        'wizards/esg_report_wizard_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ecosphere_esg/static/src/js/esg_dashboard.js',
            'ecosphere_esg/static/src/xml/esg_dashboard.xml',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
