# -*- coding: utf-8 -*-
from openerp.osv import fields, orm


class product_product(orm.Model):
    _inherit = 'product.product'

    _columns = {
        'part_number': fields.char(u"Part number",
                                   help=u"Colonne PART NUMBER du fichier Excel"),
    }
