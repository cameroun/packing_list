# -*- coding: utf-8 -*-
import time
from openerp.osv import fields, orm, osv
from openerp import netsvc
from openerp import tools
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class packing_list(orm.Model):
    _name = 'packing.list'
    _rec_name = 'pl_no'
    _inherit = ['mail.thread']

    _columns = {
        'res_partner_id': fields.many2one('res.partner', u"Société",
                                          track_visibility='onchange',
                                          help=u"Champ SOCIETE du fichier Excel"),
        'pl_no': fields.char(u"P/L No",
                             help=u"Champ P/L No. du fichier Excel"),
        'contrat': fields.char(u"Contrat", track_visibility='onchange',
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
                                       track_visibility='onchange',
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
    _defaults = {
        'state': 'draft',
    }

    # Fonctions liées aux workflows

    def action_confirm(self, cr, uid, ids, context=None):
        """ Valide les données importées.
        @return: True
        """
        if isinstance(ids, (int, long)):
            ids = [ids]
        self.write(cr, uid, ids, {'state': 'confirmed'})

        return True

    def action_done(self, cr, uid, ids, context=None):
        """Change l'etat de la liste de colisage à done.
        Cette methode est appellée à la fin du workflow par l'activité "done"

        @return: True
        """
        if isinstance(ids, (int, long)):
            ids = [ids]
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
        if isinstance(ids, (int, long)):
            ids = [ids]
        self.write(cr, uid, ids, {'state': 'cancel', })
        return True

    def draft_confirmed(self, cr, uid, ids, *args):
        """ Passe l'état de la liste de colisage de brouillon à confirmé
        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        for pack in self.browse(cr, uid, ids):
            if pack.state == 'draft':
                res = wf_service.trg_validate(uid, 'packing.list', pack.id, 'button_confirm', cr)
        return res

    def confirmed_done(self, cr, uid, ids, *args):
        """ Passe l'état de la liste de colisage de confirmé à done
        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        for pack in self.browse(cr, uid, ids):
            if pack.state == 'confirmed':
                res = wf_service.trg_validate(uid, 'packing.list', pack.id, 'button_done', cr)
        return res

    def test_finished(self, cr, uid, ids):
        """ Test si une liste de colisage est à l'état done ou cancel ou pas
        @return: True or False
        """
        for packing in self.browse(cr, uid, ids):
            if packing.state in ('done', 'cancel'):
                return False
            else:
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
                    u"""Vous ne pouvez pas annuler une liste de colisage dont les stocks
    ont déjà été mise à jour""")

    # Fin des fonctions liées au wkf

    def get_all_product_box_qty_ids(self, cr, uid, box_ids, context=None):
        """
        Retourne la liste des ids et des quantitées des produits disponibles
        dans une liste de colisage, donc dans tous les box
        Cette fonctionne nous retourne une liste de browse du modele product.box.quantity

        @param box_ids: browse des box de la liste de colisage (packing.list)
        @rtype: list
        """
        product_box_qty_ids = []
        for box in box_ids:
            product_box_qty_ids.extend(box.product_box_qty_ids)
        return product_box_qty_ids

    def change_product_qty(self, cr, uid, product_ids_qty, context=None):
        """ Changes the Product Quantity by making a Physical Inventory.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param product_ids_qty: dict content all product_id and new quantity
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}

        inventry_obj = self.pool.get('stock.inventory')
        inventry_line_obj = self.pool.get('stock.inventory.line')
        prod_obj_pool = self.pool.get('product.product')

        for product_id, product_qty in product_ids_qty.iteritems():
            res_original = prod_obj_pool.browse(cr, uid, product_id, context=context)
            if product_qty < 0:
                raise osv.except_osv(u"Erreur!", u"La quantité de doit pas être négative")
            inventory_id = inventry_obj.create(
                cr,
                uid,
                {'name': ('%s') % tools.ustr(res_original.name)},
                context=context
            )
            line_data = {
                'inventory_id': inventory_id,
                'product_qty': product_qty,
                'location_id': context['location'],
                'product_id': product_id,
                'product_uom': res_original.uom_id.id,
                # 'prod_lot_id': data.prodlot_id.id
            }
            inventry_line_obj.create(cr, uid, line_data, context=context)

            inventry_obj.action_confirm(cr, uid, [inventory_id], context=context)
            inventry_obj.action_done(cr, uid, [inventory_id], context=context)

        # On change passe l'état de la liste de colisage à done si tout se passe bien
        pack_ids = [context['packing_list_id']] if 'packing_list_id' in context else []
        self.action_done(cr, uid, pack_ids, context)
        return {}

    def update_stock_qty(self, cr, uid, ids, context=None):
        """
        Cette fonction parcour la liste des box de la liste de colisage concernée et
        import les quantités de produit dans l'emplacement de stock concerné
        """
        new_product_ids_qty = {}
        for pack in self.browse(cr, uid, ids):
            if not pack.location_id:
                raise osv.except_osv(
                    u"Erreur",
                    u"Vous devez spécifier un emplacement de stock "
                    u"pour effectuer cette opération"
                )
            all_product_box_qty_ids = self.get_all_product_box_qty_ids(
                cr,
                uid,
                pack.product_box_ids
            )
            # On recupère l'ancienne quantité de chaque produit
            context['location'] = pack.location_id.id
            context['packing_list_id'] = pack.id
            # On crée les lignes de mouvement de stock
            for product_box_qty in all_product_box_qty_ids:
                new_product_qty = product_box_qty.quantity + \
                    product_box_qty.product_id.qty_available
                new_product_ids_qty[product_box_qty.product_id.id] = new_product_qty
            self.change_product_qty(cr, uid, new_product_ids_qty, context)
