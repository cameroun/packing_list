# -*- coding: utf-8 -*-
from openerp.osv import fields, orm


class packing_list(orm.Model):
    _name = 'packing.list'
    _rec_name = 'pl_no'

    _columns = {
        'res_company_id': fields.many2one('res.company', u"Société",
                                          help=u"Champ SOCIETE du fichier Excel"),
        'pl_no': fields.char(u"P/L No",
                             help=u"Champ P/L No. du fichier Excel"),
        'contrat': fields.char(u"Contrat",
                               help=u"Champ CONTRAT du fichier Excel"),
        'invoice_num': fields.char(u"Invoice No.",
                                   help=u"Champ INVOICE No. du fichier Excel"),
        'date': fields.datetime(u"Date",
                                help=u"Champ DATE du fichier Excel"),
        'lc_no': fields.char(u"L/C No.",
                             help=u"Champ L/C No. du fichier Excel"),
        'po_no': fields.char(u"P/O No",
                             help=u"Champ P/O No. du fichier Excel"),
        'project': fields.char(u"Projet",
                               help=u"Champ PROJECT du fichier Excel"),
        'pu_no': fields.char(u"PU No.",
                             help=u"Champ PU No. du fichier Excel"),
        'to': fields.char('TO', help=u"Destinataire de la liste de colisage"),
        'product_box_ids': fields.one2many('product.box', 'packing_list_id', u"Box",
                                           help=u"Liste des box de la liste de colisage"),
        'location_id': fields.many2one('stock.location', u"Emplacement",
                                       help=u""" C'est dans cet emplacement que les quantités
    de produits liées à cette liste de colisage seront mise à jour"""),


    }
