{
    "name": "POS Event Pass - Téléphone sur le reçu",
    "summary": "Affiche le téléphone du client sur le reçu de pass (Point de Vente)",
    "author": "Moka",
    "website": "https://www.moka.cloud",
    "category": "Point of Sale",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["pos_event_pass"],
    "assets": {
        "point_of_sale.assets": [
            "pos_event_pass_phone/static/src/xml/**/*.xml",
        ]
    },
    "installable": True,
    "auto_install": False,
}
