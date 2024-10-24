# -*- coding: utf-8 -*-
{
    'name': 'Sale Event Pass',
    'version': '16.0.1.0.0',
    'category': 'Event',
    "author": "Moka",
    "website": "https://www.moka.cloud",
    'summary': 'Sale Event Pass',
    'description': "Sale Event Pass",
    'depends': ['sale', 'event_pass'],
    'installable': True,
    'auto_install': True,
    'license': 'AGPL-3',
    "data": {
        'security/ir.model.access.csv',
        'views/event_pass_line.xml',
        'views/pass_menu_views.xml',
        'data/mail_template_data.xml'
    }
}
