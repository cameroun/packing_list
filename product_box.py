# -*- coding: utf-8 -*-

from openerp.osv import fields, orm


class product_box(orm.Model):
    """
    Modélisation d'un box, contenant des articles et liés à une liste de colisage
    """
    _name = 'product.box'
    _description = u"Box contenant des produits"

    _columns = {
        'name': fields.char(u"BOX NAME", help=u"Colonne BOX NAME du fichier Excel",
                            required=True),
        'case_no': fields.char(u"CASE. NO.", help=u"Colonne CASE. NO. du fichier Excel"),
        'material': fields.char(u"MATERIAL", help=u"Colonne MATERIAL du fichier Excel"),
        'gw': fields.char(u"GW (KG)", help=u"Colonne GW(KG) du fichier Excel"),
        'nw': fields.char(u"NW (KG)", help=u"Colonne NW(KG) du fichier Excel"),
        'size': fields.char(u"Size", help=u"Colonne SIZE du fichier Excel"),
        'volume': fields.char(u"Volume", help=u"Colonne VOLUME du fichier Excel"),
        'note': fields.text(u"Note", help=u"Colonne NOTE du fichier Excel"),
        'packing_list_id': fields.many2one('packing.list', u"Liste de colisage", required=True),
        'product_box_qty_ids': fields.one2many('product.box.quantity', 'product_box_id',
                                               u"Quantité produit/Box",
                                               help=u"Quantité de produit par box"),
    }
