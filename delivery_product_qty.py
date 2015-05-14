# -*- coding: utf-8 -*-
from openerp.osv import fields, orm


class DeliveryProductQty(orm.Model):
    """
    Utiliser pour représenter les différents produits (y compris la qté)
    extraits d'un box donnée.
    """
    _name = 'delivery.product.qty'
    _rec_name = 'product_id'
    _columns = {
        'delivery_note_line_id': fields.many2one('delivery.note.line', u"Delivery note line"),
        'product_id': fields.many2one('product.product', u"Article"),
        'qty': fields.float(u"Quantité"),
    }
