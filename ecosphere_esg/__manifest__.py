{
    'name': 'EcoSphere ESG',
    'version': '18.0.2.0.0',
    'category': 'Sustainability',
    'summary': 'ESG Management Platform',
    'description': """
        ESG Management Platform for tracking carbon emissions,
        emission factors, compliance issues, department rankings,
        and smart sustainability dashboards.
    """,
    'author': 'EcoSphere',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'data/demo_data.xml',
        'views/esg_views.xml',
        'views/department_views.xml',
        'views/dashboard_views.xml',
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
