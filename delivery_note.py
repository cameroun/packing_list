# -*- coding: utf-8 -*-

from openerp.osv import fields, orm


class DeliveryNote(orm.Model):
    _name = 'delivery.note'
    _rec_name = ''
    _inherit = ['mail.thread']

    _columns = {
        'purpose': fields.char(u"Purpose of delivery"),
        'address': fields.text(u"Delivery address"),
        'site': fields.char(u"Site"),
        'contract_info': fields.char(u"Contract Info"),
        'project_name': fields.char(u"Project name"),
        'project_code': fields.char(u"Project code"),
        'product_categorie': fields.many2one('product.category', u"Product categiry"),
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
        # section Partial case handling
        'packing_list_id': fields.many2one('packing.list', u"Package Name"),
    }
