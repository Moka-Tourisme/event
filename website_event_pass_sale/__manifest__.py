{
    "name": "Website Event Pass Sale",
    "summary": "Website Event Pass Sale",
    "author": "Moka",
    "website": "https://www.mokatourisme.fr",
    "category": "Others",
    "version": "15.0.0.0.0",
    'summary': 'Sell event passes through products on the website',
    'depends': ['website_sale', 'sale_event_pass'],
    'data': [
        'views/event_pass_views.xml',
        'views/templates.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}