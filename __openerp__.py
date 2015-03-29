# ==============================================================================
#                                                                             =
#    connector_skipper module for Odoo
#    Copyright (C) 2015 Anybox (<http://anybox.fr>)
#                                                                             =
#    connector_skipper is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License v3 or later
#    as published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#                                                                             =
#    connector_skipper is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License v3 or later for more details.
#                                                                             =
#    You should have received a copy of the GNU Affero General Public License
#    v3 or later along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#                                                                             =
# ==============================================================================
{
    'name': 'HUAWEI Packing List',
    'version': '0.1',
    'description': """
HUAWEI Packing List
===================
Gestion des listes de colisage

    """,
    'summary': "Gestion des listes de colisage",
    'icon': '/connector_skipper/static/description/icon.png',
    'author': 'Odoo Cameroun',
    'website': 'http://odoo-cameroun.com',
    'license': 'AGPL-3',
    'category': 'Product Management',
    'depends': ['base', 'purchase',
                'stock', 'product',
                'delivery', ],
    'external_dependencies': {
        'python': ['unidecode'],
    },
    'data': [
        'security/ir.model.access.csv',
        'menu.xml',
        'views/packing_list_view.xml',
        'views/product_box_view.xml',
    ],
    'demo': [
    ],
    'auto_install': False,
    'web': False,
    'post_load': None,
    'application': False,
    'installable': True,
    'sequence': 150,
}
