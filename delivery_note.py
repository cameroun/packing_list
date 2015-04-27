# -*- coding: utf-8 -*-
import time

from openerp.osv import fields, orm, osv
from openerp import netsvc
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
        'dn_no': fields.char(u"DN No.", track_visibility='onchange'),
        'mr_no': fields.char(u"MR No.", track_visibility='onchange'),
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


class DeliveryNoteLine(orm.Model):
    _name = 'delivery.note.line'

    def _get_name(self, cr, uid, ids, fields_name, arg, context):
        """
        Le nom des deliveru_note_line est une concaténation entre le nom de la
        liste de colisage et le numéro du box. Ceci sera utilisé pour l'affichage dans l'interface
        """
        result = dict()
        for note_line in self.browse(cr, uid, ids, context):
            packing_list_name = note_line.packing_list_name or ""
            box_no = note_line.box_no or ""
            name = packing_list_name + "-" + box_no
            result[note_line.id] = name
        return result

    _columns = {
        'name': fields.function(_get_name, type='char', string='Name', readonly=True),
        'cl_no': fields.char(u"C/L No."),
        'packing_list_name': fields.char(u"Package Name"),
        'actual_packing_list_name': fields.char(u"Actual package name"),
        'box_no': fields.char(u"Box No."),
        'box_type': fields.char(u"Box Type"),
        'weight': fields.float(u"Weight (KG)"),
        'volume': fields.float(u"Volume (CBM)"),
        'model_desc': fields.text(u"Model/Model Desc/Version"),
        'box_status': fields.char(u"Box Status"),
        'locator': fields.char(u"Locator/LSP Locator"),
        'delivery_note_id': fields.many2one('delivery.note', u"Delivery Note"),
        'quantity': fields.integer(u"Quanttité"),
        'product_id': fields.many2one('product.product', u"Article"),
    }
