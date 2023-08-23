# -*- coding: utf-8 -*-
{
    'name': 'Website Event Link Portal',
    'version': '15.0.1.0.0',
    'category': 'Custom',
    'summary': 'Website Event Link Portal',
    'description': "Add a link when registering for an event to retrieve the ticket in the portal view",
    'depends': ['website_event_sale', 'event_portal_ticket', 'website_event_link_portal'],
    'installable': True,
    'auto_install': True,
    'license': 'AGPL-3',
    "data": {
        'data/mail_template.xml',
        'views/website_sale_confirmation.xml',
    }
}
