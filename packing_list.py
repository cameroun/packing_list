# -*- coding: utf-8 -*-
import time
from openerp.osv import fields, orm, osv
from openerp import netsvc
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


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
        'date_done': fields.datetime(
            u"Date du stansfert",
            help=u"""Date d'achèvement: C'est la date à laquelle le stock de cette liste
    de colisage a été mis à jour""",
            states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
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

    def action_confirm(self, cr, uid, ids, context=None):
        """ Valide les données importées.
        @return: True
        """
        self.write(cr, uid, ids, {'state': 'confirmed'})
        return True

    def action_done(self, cr, uid, ids, context=None):
        """Change l'etat de la liste de colisage à done.
        Cette methode est appellée à la fin du workflow par l'activité "done"

        @return: True
        """
        for packing in self.browse(cr, uid, ids, context=context):
            values = {
                'state': 'done'
            }
            if not packing.date_done:
                values['date_done'] = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            packing.write(values)
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        """ Change l'état d'une liste de colisage en Annulée.

        @return: True
        """
        self.write(cr, uid, ids, {'state': 'cancel', })
        return True

    def action_assign(self, cr, uid, ids, *args):
        """ Changes state of picking to available if all moves are confirmed.
        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        for pack in self.browse(cr, uid, ids):
            if pack.state == 'draft':
                wf_service.trg_validate(uid, 'packing.list', pack.id, 'button_confirm', cr)
        return True

    def test_finished(self, cr, uid, ids):
        """ Test si une liste de colisage est à l'état done ou cancel ou pas
        @return: True or False
        """
        for packing in self.browse(cr, uid, ids):
            if packing.state not in ('done', 'cancel'):
                if not packing.date_done:
                    return False
                else:
                    packing.write({'state': 'done'})
        return True

    def allow_cancel(self, cr, uid, ids, context=None):
        """ Vérifie si on peut annuler une liste de colisage
        @return: True
        """
        for pack in self.browse(cr, uid, ids, context=context):
            if pack.state not in ('done', 'cancel'):
                return True
            else:
                osv.except_osv(
                    u"Erreur",
                    u"""Vous ne pouvez pas annuler un liste de colisage dont les stocks
    ont déjà été mise à jour""")

    def draft_validate(self, cr, uid, ids, context=None):
        """ Valide les listes de colisages en brouillon.
        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        for pack_list in self.browse(cr, uid, ids, context=context):
            wf_service.trg_write(uid, 'packing.list', pack_list.id, cr)
        return {
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_id': ids[0],
            'res_model': 'packing.list',
            'type': 'ir.actions.act_window',
            'context': context,
            'nodestroy': True,
        }

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
