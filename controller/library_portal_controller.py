# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class CustomPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'portal_library' in counters:
            values['portal_library'] = request.env[
                'library.book'].sudo().search_count([])
        return values
    @http.route('/library_management' ,type='http', auth="user", website=True)
    def portal_library(self, search=None, search_in='All'):
        """To search all the books created by the user, admin or portal user"""

        user_books = self.env['library.book'].sudo().search([('create_uid','=',self.env.user.id)])

        return request.render('library_management.portal_my_home_contribution_views',
                              {
                                  'books': user_books,
                                  'page_name': 'library_management',
                              })

