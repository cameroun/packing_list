# -*- coding: utf-8 -*-
from openerp.osv import fields, orm, osv


class packing_list(orm.Model):
    _name = 'packing.list'
    _rec_name = 'pl_no'
    _inherit = ['mail.thread']

    _columns = {
        'res_partner_id': fields.many2one('res.partner', u"Société",
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
        'state': fields.selection(
            [('draft', u"Brouillon"),
             ('confirmed', u"Validé"),
             ('done', u"Stock mis à jour"),
             ('cancel', u"Annulé"), ],
            'Etat', readonly=True, select=True, track_visibility='onchange',
            help=u"""* Brouillon: Pas encore validé et ne sera pas traité avant d'être validé.\n
        * Validé: Les données importées sont correctes, on passe donc la liste de colisage de. \n
                  l'état Brouillon à l'état Validé afin de faire la mise à jour du stock\n
        * Stock mis à jour: Les différentes quantités de produits contenues dans les \n
                            box de la liste de colisage ont été utilisées pour faire la
                            mise à jour du stock.
                            C'est l'état finale et cette action est irréverssible.\n
        * Annulé: A été annulé, ne peut plus être validé\n"""),
    }
    _default = {
        'state': 'draft',
    }

    def validate_packing_list(self, cr, uid, ids, context=None):
        pass

    def update_stock_qty(self, cr, uid, ids, context=None):
        """
        Cette fonction parcour la liste des box de la liste de colisage concernée et
        import les quantités de produit dans l'emplacement de stock concerné
        """
        for pack_list in self.browse(cr, uid, ids):
            if not pack_list.location_id:
                raise osv.except_osv(
                    u"Erreur lors de la mise à jour du stock",
                    u"Vous devez spécifier un emplacement de stock "
                    u"pour effectuer cette opération"
                )
