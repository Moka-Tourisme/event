# -*- coding: utf-8 -*-
{
    'name': 'Website Event Ticket Order',
    'version': '15.0.1.0.0',
    'category': 'Custom',
    'summary': 'Website Event Ticket Order',
    'description': "Organize event tickets order",
    'depends': ['event_ticket_order', 'website_event'],
    'installable': True,
    'auto_install': True,
    'license': 'AGPL-3',
    "data": {
        'views/event_ticket_order.xml',
    }
}
