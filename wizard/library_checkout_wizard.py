# -*- coding: utf-8 -*-
from odoo import fields, models, api


class LibraryCheckoutWizard(models.TransientModel):
    _name = 'library.checkout.wizard'
    _description = 'Library Checkout Wizard'

    book_id = fields.Many2one('library.book', string='Book')
    book_ids = fields.Many2many('library.book', string='Books')

    @api.model
    def default_get(self, fields_list):
        """recommend books for checkout wizard"""
        res = super().default_get('fields_list')

        rec_books = self.sudo().env.context.get('all_book_id')

        if rec_books:
            book = self.sudo().env['library.book'].browse(rec_books)

            book_count = self.sudo().env['library.checkout.line'].search([])
            book_wise_count = {}
            for i in book_count:
                if i.book_id.sudo().status == 'available':
                    name = i.book_id.name
                    book_wise_count[name] = book_wise_count.get(name, 0) + 1

            sorted_by_value_desc = {k: v for k, v in
                                    sorted(book_wise_count.items(), key=lambda item: item[1], reverse=True)}
            each_count = sorted_by_value_desc.values()
            if each_count:
                max_count = max(each_count)
            else:
                max_count = 0
            keys = [key for key, val in sorted_by_value_desc.items() if val == max_count]
            print(keys)

            print("total books:", sorted_by_value_desc.items())
            print("max books:", max_count)

            books = book.search([('id', '!=', book), ('status', '=', 'available'),
                                 '|', '|',
                                 ('book_author_id', '=', book.book_author_id),
                                 ('genres_id', '=', book.genres_id),
                                 ('name', '=', keys)
                                 ])

            res['book_ids'] = [fields.Command.set(books.ids, )]
        return res

    def add_checkout_action(self):
        """adding books to the checkout line"""
        add_checkout = self.env.context.get('checkout')

        if add_checkout:

            checkout = self.env['library.checkout'].browse(add_checkout)
            lines = []
            for record in self.book_ids:
                lines.append((0, 0, {'book_id': record.id},))

            checkout.write({'checkout_line_ids': lines})

            return True
