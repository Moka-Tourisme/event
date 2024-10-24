{
    "name": "Event Pass",
    "summary": "Event Pass",
    "author": "Moka",
    "website": "https://www.moka.cloud",
    "category": "Event",
    "version": "16.0.0.0.1",
    "license": "AGPL-3",
    "depends": [
        "contacts",
        "event",
        "event_session",
        "barcodes",
        "mail",
        "sale"
    ],
    "data": [
        'security/ir.model.access.csv',
        'reports/pass_template.xml',
        'data/default_barcode_patterns.xml',
        'data/event_pass_cron.xml',
        'wizards/wizard_pass_line.xml',
        'views/event_pass_line.xml',
        'views/event_registration.xml',
        'views/res_partner_pass.xml',
        'views/pass_menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'event_pass/static/src/xml/create_pass_multi_view.xml',
            'event_pass/static/src/js/create_pass_multi_view.js',
        ],
    },
}
