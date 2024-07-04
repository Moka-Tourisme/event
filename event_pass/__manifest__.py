{
    "name": "Event Pass",
    "summary": "Event Pass",
    "author": "Moka",
    "website": "https://www.mokatourisme.fr",
    "category": "Others",
    "version": "15.0.0.1.0",
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
        'views/event_pass_line.xml',
        'views/event_registration.xml',
        'views/res_partner_pass.xml',
        'reports/pass_template.xml',
        'data/default_barcode_patterns.xml',
        'views/pass_menu_views.xml',
        'data/event_pass_cron.xml',
        'wizards/wizard_pass_line.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'event_pass/static/src/js/**/*',
        ],
        'web.assets_qweb': [
            'event_pass/static/src/xml/**/*',
        ],
    },
}
