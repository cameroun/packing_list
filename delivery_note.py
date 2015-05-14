# -*- coding: utf-8 -*-
import time

from openerp.osv import fields, orm, osv
from openerp import netsvc
from openerp import tools
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class DeliveryNote(orm.Model):
    _name = 'delivery.note'
    _rec_name = 'dn_no'
    _inherit = ['mail.thread']

    def _get_delivery_note_line_number(self, cr, uid, ids, fields_name, arg, context):
        """
        Retourne le nombre de box contenu dans la delivery note.
        Ceci est juste utilisé pour l'affichage
        """
        pass

    _columns = {
        'dn_no': fields.char(u"DN No.", track_visibility='onchange', required=True),
        'mr_no': fields.char(u"MR No.", track_visibility='onchange'),
        'purpose': fields.char(u"Purpose of delivery"),
        'address': fields.text(u"Delivery address"),
        'site': fields.char(u"Site"),
        'contract_info': fields.char(u"Contract Info"),
        'project_name': fields.char(u"Project name"),
        'project_code': fields.char(u"Project code"),
        'product_category_id': fields.many2one('product.category', u"Product category"),
        'special_unloading': fields.char(u"Special Unloading Req"),
        'install_env': fields.text(u"Installation Environment"),
        'description_mr': fields.text(u"Description (MR)"),
        'description_dn': fields.text(u"Description (DN)"),
        'from_warehouse': fields.many2one('stock.location', u"From warehouse"),
        'warehouse_keeper': fields.many2one('res.partner', u"Warehouse Keeper"),
        'receiver': fields.many2one('res.partner', u"Receiver"),
        'site_address': fields.text(u"Site address"),
        'request_arrived_date': fields.datetime(u"Request Arrived Date"),
        'request_shipment_date': fields.datetime(u"Request Shipment Date"),
        'print_date': fields.datetime(u"Print Date"),
        'logistics_specialist': fields.many2one('res.partner', u"Logistics Specialist"),
        'customer': fields.many2one('res.partner', u"Customer"),
        'product_manager': fields.many2one('res.partner', u"Product Manager"),
        'state': fields.selection(
            [('draft', u"Brouillon"),
             ('confirmed', u"Validé"),
             ('done', u"Stock mis à jour"),
             ('cancel', u"Annulé"), ],
            'Etat', readonly=True, select=True, track_visibility='onchange',
            help=u"""* Brouillon: Pas encore validé et ne sera pas traité avant d'être validé.\n
    * Validé: Les données importées (ou créées) sont correctes, on passe donc la delivery \n
    note de l'état Brouillon à l'état Validé afin de faire la mise à jour du stock\n
    * Stock mis à jour: Les différentes quantités de produits contenues dans les \n
        box de la liste de colisage ont été utilisées pour faire la  mise à jour du stock.
        C'est l'état finale et cette action est irréverssible.\n
     * Annulé: A été annulé, ne peut plus être validé\n"""),
        'date_done': fields.datetime(
            u"Date du stansfert",
            help=u"""Date d'achèvement: C'est la date à laquelle le stock de des produits contenus
    dans la delivery note a été mis à jour""",
            states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}),
        # section Partial case handling
        'delivery_note_line_ids': fields.one2many(
            'delivery.note.line',
            'delivery_note_id', u"Delivery note line",
            help=u"section Partial case handling"),
        # Signature
        'applicant': fields.char(u"Applicant"),
        'approver': fields.char(u"Approver"),
        'issued_by': fields.char(u"Issued By"),
        'applicant_date': fields.datetime(u"Applicant Date"),
        'approver_date': fields.datetime(u"Approver Date"),
        'issued_date': fields.datetime(u"Issued Date"),
        'signe_by': fields.char(u"Signed by"),
        'creator': fields.char(u"Creator"),
        'driver': fields.char(u"Driver"),
        'creator_company': fields.many2one('res.partner', u"Creator Dept/Company"),
        'driver_company': fields.many2one('res.partner', u"Driver Dept/Company"),
        'creator_date': fields.datetime(u"Creator Date"),
        'driver_date': fields.datetime(u"Driver Date"),
        'carrier': fields.many2one('res.partner', u"Carrier"),
        'carrier_contact': fields.many2one('res.partner', u"Carrier contact"),
        # Pour l'affichage
        'delivery_note_line_number': fields.function(
            _get_delivery_note_line_number,
            type="integer",
            string=u"Total Box"
        ),
    }

    _defaults = {
        'state': 'draft',
    }

    # Fonctions liées aux workflows

    def action_confirm(self, cr, uid, ids, context=None):
        """ Valide les données crées/importées.
        @return: True
        """
        if isinstance(ids, (int, long)):
            ids = [ids]
        self.write(cr, uid, ids, {'state': 'confirmed'})

        return True

    def action_done(self, cr, uid, ids, context=None):
        """Change l'etat de la delivery note à done.
        Cette methode est appellée à la fin du workflow par l'activité "done"

        @return: True
        """
        if isinstance(ids, (int, long)):
            ids = [ids]
        for delivery in self.browse(cr, uid, ids, context=context):
            values = {
                'state': 'done'
            }
            if not delivery.date_done:
                values['date_done'] = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            delivery.write(values)
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        """ Change l'état de la delivery note en Annulée.

        @return: True
        """
        if isinstance(ids, (int, long)):
            ids = [ids]
        self.write(cr, uid, ids, {'state': 'cancel', })
        return True

    def draft_confirmed(self, cr, uid, ids, *args):
        """ Passe l'état de la delivery note de brouillon à confirmé
        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        for deliv in self.browse(cr, uid, ids):
            if deliv.state == 'draft':
                res = wf_service.trg_validate(
                    uid, 'delivery.note', deliv.id, 'button_confirm_dn', cr
                )
        return res

    def confirmed_done(self, cr, uid, ids, *args):
        """ Passe l'état de la delivery note de confirmé à done
        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        for deliv in self.browse(cr, uid, ids):
            if deliv.state == 'confirmed':
                res = wf_service.trg_validate(uid, 'delivery.note', deliv.id, 'button_done', cr)
        return res

    def test_finished(self, cr, uid, ids):
        """ Test si une delivery note est à l'état done ou cancel ou pas
        @return: True or False
        """
        for deliv in self.browse(cr, uid, ids):
            if deliv.state in ('done', 'cancel'):
                return False
            else:
                if not deliv.date_done:
                    return False
                else:
                    deliv.write({'state': 'done'})
        return True

    def allow_cancel(self, cr, uid, ids, context=None):
        """ Vérifie si on peut annuler une delivery note
        @return: True
        """
        for deliv in self.browse(cr, uid, ids, context=context):
            if deliv.state not in ('done', 'cancel'):
                return True
            else:
                osv.except_osv(
                    u"Erreur",
                    u"""Vous ne pouvez pas annuler une delivery note dont les stocks
    ont déjà été mise à jour""")

    # Fin des fonctions liées au wkf

    def _check_packing_list_location(self, cr, uid, packing_list_id):
        """
        Verifie si un emplacement de stock est défini sur la liste de colisage
        """
        pass

    def _get_box_id(self, cr, uid, box_field, field_value):
        """
            Retourne l'id d'un box en recherchant une valeur sur un champ donner
        """
        box_mdl = self.pool.get('product.box')
        if not (box_field or field_value):
            return False
        return box_mdl.search(cr, uid, [(box_field, '=', field_value)])

    def get_all_delevery_product_qty_ids(self, cr, uid, delivery_note_line_ids, context=None):
        """
        Retourne la liste des ids et des quantitées des produits disponibles
        dans un delivery note, donc dans tous les box
        Cette fonction nous retourne une liste de browse du modele delivery.product.qty

        @param delivery_note_line_ids: browse des box de la liste de la delivery.note.line
        @rtype: list
        """
        delevery_product_qty_ids = []
        for line in delivery_note_line_ids:
            delevery_product_qty_ids.extend(line.delivery_product_qty_ids)
        return delevery_product_qty_ids

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
            }
            inventry_line_obj.create(cr, uid, line_data, context=context)

            inventry_obj.action_confirm(cr, uid, [inventory_id], context=context)
            inventry_obj.action_done(cr, uid, [inventory_id], context=context)

        # On change passe l'état de la delivery note à done si tout se passe bien
        delivery_ids = [context['delivery_note_id']] if 'delivery_note_id' in context else []
        self.action_done(cr, uid, delivery_ids, context)
        return {}

    def update_stock_qty(self, cr, uid, ids, context=None):
        """
        Cette fonction parcour la liste les ligne de la delivery note et
        import les quantités de produit dans l'emplacement de stock
        (champ from_warehouse)
        """
        new_product_ids_qty = {}
        for deliv in self.browse(cr, uid, ids):
            if not deliv.from_warehouse:
                raise osv.except_osv(
                    u"Erreur",
                    u"Vous devez spécifier un emplacement de stock "
                    u"pour effectuer cette opération \n"
                    u"[Champ 'From warehouse']"
                )
            all_delivery_product_ids = self.get_all_delevery_product_qty_ids(
                cr, uid, deliv.delivery_note_line_ids
            )
            # On recupère l'ancienne quantité de chaque produit
            context['location'] = deliv.from_warehouse.id
            context['delivery_note_id'] = deliv.id
            # On crée les lignes de mouvement de stock
            for delivery_product_qty in all_delivery_product_ids:
                new_product_qty = delivery_product_qty.product_id.qty_available - \
                    delivery_product_qty.qty
                new_product_ids_qty[delivery_product_qty.product_id.id] = new_product_qty
            self.change_product_qty(cr, uid, new_product_ids_qty, context)
