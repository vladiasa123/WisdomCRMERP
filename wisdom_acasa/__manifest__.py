{
    "name": "Wisdom Acasa",
    "version": "18.0.1.0.0",
    "category": "Web",
    "summary": "Custom homepage Acasa with menu shortcuts",
    "description": """
        Adds a top-level 'Acasa' menu in Odoo 18 with custom dashboard shortcuts.
    """,
    "author": "Your Name / Company",
    "website": "https://yourcompany.com",
    "license": "LGPL-3",
    "depends": ["base", "web"],
    "data": [
        "views/acasa_menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "wisdom_acasa/static/src/js/acasa_homepage.js",
            "wisdom_acasa/static/src/xml/acasa_template.xml",
            "wisdom_acasa/static/src/css/acasa_style.css",
        ],
    },
    "application": True,
    "installable": True,
}
