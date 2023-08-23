# -*- coding: utf-8 -*-
{
    'name': 'Website Event Link Portal',
    'version': '15.0.1.0.0',
    'category': 'Custom',
    'summary': 'Website Event Link Portal',
    'description': "Add a link when registering for an event to retrieve the ticket in the portal view",
    'depends': ['website_event', 'event_portal_ticket'],
    'installable': True,
    'auto_install': True,
    'license': 'AGPL-3',
    "data": {
        'views/event_registration.xml',
    }
}
