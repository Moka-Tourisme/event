{
    'name': 'Events Portal',
    'version': '16.0.0.0.1',
    'category': 'Events',
    'summary': 'List of all events',
    'author': 'Moka Tourisme',
    'description': "List of all events",
    'depends': ['event', 'portal'],
    'data': [
        'security/account_security.xml',
        'security/ir.model.access.csv',
        'views/event_portal_templates.xml',
        'report/event_portal_report.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'event_portal/static/src/js/event_portal_sidebar.js',
        ]
    },
    'installable': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
