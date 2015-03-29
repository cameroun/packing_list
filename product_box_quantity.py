# -*- coding: utf-8 -*-
# flake8: noqa

from openerp.osv import fields, orm


class product_box_quantity(orm.Model):
    """
    Cette classe nous permettra de stocker la quantité de
    chaque produit présent dans un box
    """
    _name = 'product.box.quantity'
    _rec_name = 'product_box_id'
    _description = u"Quantité de produit dans chaque box"

    _columns = {
        'product_box_id': fields.many2one('product.box', u"Box",
                                          help=u"Box présent dans la liste de colisage"),
        'quantity': fields.integer(u"Quanttité"),
        'product_id': fields.many2one('product.product', u"Article"),
    }
