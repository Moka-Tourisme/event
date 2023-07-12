# -*- coding: utf-8 -*-
{
    'name': 'Events Portal',
    'version': '15.0.0.1.0',
    'category': 'Events',
    'summary': 'List of all events',
    'description': "List of all events",
    'depends': ['event', 'portal', 'event_session'],
    'data': [
        'security/account_security.xml',
        'security/ir.model.access.csv',
        'views/event_portal_templates.xml',
        'views/event_sessions_portal_templates.xml',
        'views/content_template.xml',
        'report/event_portal_report.xml',
        'report/session_portal_report.xml',
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
