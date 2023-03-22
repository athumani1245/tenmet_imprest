# -*- coding: utf-8 -*-
# from odoo import http


# class TenmetImprest(http.Controller):
#     @http.route('/tenmet_imprest/tenmet_imprest/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tenmet_imprest/tenmet_imprest/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tenmet_imprest.listing', {
#             'root': '/tenmet_imprest/tenmet_imprest',
#             'objects': http.request.env['tenmet_imprest.tenmet_imprest'].search([]),
#         })

#     @http.route('/tenmet_imprest/tenmet_imprest/objects/<model("tenmet_imprest.tenmet_imprest"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tenmet_imprest.object', {
#             'object': obj
#         })
