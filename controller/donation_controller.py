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
        condition=kwargs['condition']
        image_files=kwargs['book_image']
        image_file = request.httprequest.files.getlist('book_image')
        if image_files:
            image = base64.b64encode(image_files.read())
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
        new_record=self.env['library.book'].sudo().create({
            'name':name,
            'isbn':isbn,
            'image':image,
            'book_condition':condition,
            'book_author_id':authors.id,
            'status':'coming_soon',
        })
        if image_file:
            img_list = []
            for file in image_file:
                data=base64.b64encode(file.read())
                if data == b'':
                    continue
                else:
                    img_val = {
                        'name': file.filename,
                        'datas': data,
                        'res_model': 'library.book',
                        'res_id': new_record.id,
                    }
                    print(img_val)
                img_list.append(request.env['ir.attachment'].sudo().create(img_val).id)
                print(img_list)

                new_record.write({'book_image': [(6, 0, img_list)]})

        user_name = request.env.user.name if request.env.user.id else 'Guest'
        return request.render('library_management.success_form_template', {
           'user_name': user_name,
       })

    @http.route('/my/book/<int:book_id>', type='http', auth='user', website=True)
    def portal_book_detail(self, book_id):
        book = request.env['library.book'].sudo().browse(book_id)
        return request.render('library_management.book_detail', {'book': book})

