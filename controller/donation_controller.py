# -*- coding: utf-8 -*-
import base64
from odoo import http
from odoo.http import request


class DonationController(http.Controller):
    @http.route('/hello-odoo', type='http', auth='public', website=True)
    def hello_page(self, **kwargs):
        """
        This controller handles the request for the /hello-odoo page.
        It renders a QWeb template and passes a dynamic value.
        """
        return request.render('library_management.donation_form_template')

    @http.route('/hello-odoo', type='http', auth='public', website=True ,methods=['POST'], csrf=False)
    def donation(self, **kwargs):
        name=kwargs['name']
        author=kwargs['author']
        isbn=kwargs['isbn']
        image_file = kwargs['book_image']
        if image_file:
            image = base64.b64encode(image_file.read())
        else:
            image = None

        authors=self.env['library.author'].sudo().search([('name','=',author)])
        print(authors)
        if not authors:
            self.env['library.author'].sudo().create({
                'name':author,
            })

        is_isbn = self.env['library.book'].sudo().search([('isbn', '=', isbn)])
        if is_isbn:
            return request.render('library_management.uniqu_field_form_template')
        authors = self.env['library.author'].sudo().search([('name', '=', author)])
        print(authors)
        self.env['library.book'].sudo().create({
            'name':name,
            'isbn':isbn,
            'image':image,
            'book_author_id':authors.id,
            'status':'coming_soon',

        })
        user_name = request.env.user.name if request.env.user.id else 'Guest'
        return request.render('library_management.success_form_template', {
           'user_name': user_name,
       })