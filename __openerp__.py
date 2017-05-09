# -*- coding: utf-8 -*-
# © 2017 Igor V. Kartashov
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": 'partner WEB Form',
    "version": "9.0.1.0",
    "summary": "extensión formulario WEB para los clientes con acceso a portal",
    "description": """
		i-vk
		v9.0.1.0
		extensión formulario WEB para los clientes con el acceso a portal
	""",
    "author": "Igor V. Kartashov",
    "license": "AGPL-3",
    "website": "http://crm.setir.es",
    "category": "Partner",
    "depends": ["base",
				"partnerAssociate",
				"website",
				],
    "data": [
        "views/templates.xml",
        "views/partnerConfirm.xml",
    ],
    "installable": True,
    "application": True,
	"auto_install": False,
    "price": 0.00,
    "currency": "EUR"
}