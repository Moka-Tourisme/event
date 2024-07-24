{
    'name': 'Event Portal Ticket',
    'version': '16.0.0.0.1',
    'summary': 'List of all event tickets',
    'description': "List of all event tickets",
    'author': 'Moka Tourisme',
    'depends': ['event', 'portal', 'event_registration_qr_code', 'website_event'],
    'data': [
        'security/ir.model.access.csv',
        'security/event_portal_ticket_report.xml',
        'views/event_portal_ticket_templates.xml',
        'views/content_template.xml',
    ],

    'installable': True,
    'auto_install': True,
    'license': 'AGPL-3',
}
