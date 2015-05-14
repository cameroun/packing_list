# -*- coding: utf-8 -*-
from openerp.osv import fields, orm


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
        'box_status': fields.selection(
            (('whole', u"Whole"), ('opened', u"Opened")),
            u"Box Status",
            help=u""" Whole: correspond a un box qui n’a jamais ete ouvert; \n
    Opened: correspond a un box déjà ouvert pour prendre certains articles"""
        ),
        'locator': fields.char(u"Locator/LSP Locator"),
        'delivery_note_id': fields.many2one('delivery.note', u"Delivery Note"),
        'delivery_product_qty_ids': fields.one2many(
            'delivery.product.qty',
            'delivery_note_line_id',
            u"Article"
        ),
    }
