# -*- coding: utf-8 -*-
{
    'name': 'Event Session Portal Ticket',
    'version': '15.0.1.0.0',
    'summary': 'List of all event session tickets',
    'description': "List of all event session tickets",
    'depends': ['event_portal_ticket', 'event_session'],
    'data': [
        'security/ir.model.access.csv',
        'security/event_portal_ticket_report.xml',
        'views/event_session_portal_ticket_templates.xml',
        'views/content_template.xml',
    ],

    'installable': True,
    'auto_install': True,
    'license': 'AGPL-3',
}
