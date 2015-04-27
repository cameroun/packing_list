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
                'stock', 'product', ],
    'external_dependencies': {
        'python': ['unidecode'],
    },
    'data': [
        'security/ir.model.access.csv',
        'menu.xml',
        'views/packing_list_view.xml',
        'views/product_box_view.xml',
        'views/product_view.xml',
        'views/product_box_quantity_view.xml',
        'views/product_view.xml',
        'packing_list_workflow.xml',
        'views/delivery_note_view.xml',
        'views/delivery_note_line_view.xml',
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
