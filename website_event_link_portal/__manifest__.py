{
    'name': 'Website Event Link Portal',
    'version': '16.0.0.0.1',
    'category': 'Custom',
    'summary': 'Website Event Link Portal',
     'author': 'Moka Tourisme',
    'description': "Add a link when registering for an event to retrieve the ticket in the portal view",
    'depends': ['website_event', 'event_portal_ticket'],
    'installable': True,
    'auto_install': True,
    'license': 'AGPL-3',
    "data": {
        'views/event_registration.xml',
    }
}
