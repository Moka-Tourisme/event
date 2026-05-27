{
    'name': 'Point Of Sale Event Pass',
    'version': '16.0.1.0.0',
    "author": "Moka",
    "website": "https://www.moka.cloud",
    'category': 'Event',
    'summary': 'Point Of Sale Event Pass',
    'description': "Point Of Sale Event Pass",
    'depends': ["point_of_sale", "sale_event_pass"],
    'installable': True,
    'auto_install': True,
    'license': 'AGPL-3',
    "assets": {
        "point_of_sale.assets": [
            "pos_event_pass/static/src/js/**/*.js",
            "pos_event_pass/static/src/scss/**/*.scss",
            "pos_event_pass/static/src/xml/**/*.xml",
        ]
    },
    "data": [
        "views/event_pass_line.xml",
        "views/pos_order.xml",
    ],
}
