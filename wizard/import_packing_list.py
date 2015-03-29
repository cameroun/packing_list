# -*- coding: utf-8 -*
from openerp.osv import fields, osv


class wizard_import_packing_list(osv.TransienModel):
    """
    Ceci sera utiliser pour excéuter un script d'importation.
    En fonction de l'emplacement de stock spécifié et du fichier
    Excel sélectionné, les listes de colisages seront générees.
    """
    _name = 'wizard.packing.list'
    _description = u"Importation d'une liste de colisage"
    _columns = {
        'location_id': fields.many2one('stock.location', u"Emplacement",
                                       help=u""" C'est dans cet emplacement que les quantités
    de produits liées à cette liste de colisage seront mise à jour"""),
        'filename': fields.binary(u"Fichier",
                                  help=u"Fichier Excel a importer")
    }

    def import_packing_list(self, cr, uid, ids, context=None):
        """
        Fonction qui import la liste de colisage.
        Elle est appelée depuis un bouton du wizard
        """
        return True
